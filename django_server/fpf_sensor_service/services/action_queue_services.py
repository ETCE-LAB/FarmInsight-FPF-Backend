import asyncio

from datetime import timedelta

from django.utils.timezone import now
from asgiref.sync import sync_to_async

from fpf_sensor_service.models import ActionQueue, Hardware
from fpf_sensor_service.triggers import TriggerHandlerFactory
from fpf_sensor_service.utils import get_logger, async_safe_log
from fpf_sensor_service.action_scripts import TypedActionScriptFactory
from fpf_sensor_service.serializers import ActionQueueSerializerDescriptive
from fpf_sensor_service.scripts_base import ScriptType, TypedScript
from .action_services import get_action_by_id
from .action_trigger_services import get_all_active_auto_triggers
from .auth_services import async_get_fpf_id


typed_action_script_factory = TypedActionScriptFactory()
logger = get_logger()


def get_active_state_of_action(controllable_action_id):
    """
    Get the active state (trigger) for an action.
    (Last executed action is the currently active action)
    :param controllable_action_id:
    :return:
    """
    last_action =  ActionQueue.objects.filter(
        action__id=controllable_action_id,
        endedAt__isnull=False,
        startedAt__isnull=False,
    ).order_by('createdAt').last()

    if last_action is None:
        return None

    # For auto actions, return them always. (we check here anyway if the action has a matching isAutomated)
    action = get_action_by_id(controllable_action_id)
    if last_action.trigger.type != 'manual' and action.isAutomated:
        return last_action

    # Return manual action only if the action is in manual mode.
    # We need this to activate a manual trigger which was in auto mode.
    if last_action.trigger.type == 'manual' and not action.isAutomated:
        return last_action
    return None


def get_active_state_of_hardware(hardware_id):
    """
    Get the active state (trigger) for a hardware.
    (Last executed action is the currently active action)
    :param hardware_id:
    :return:
    """
    last_action = ActionQueue.objects.filter(
        action__hardware_id=hardware_id,
        endedAt__isnull=False,
        startedAt__isnull=False,
    ).order_by('createdAt').last()

    return last_action


def is_already_enqueued(trigger_id):
    """
    Return if the trigger is already enqueued in the queue but not started or finished yet.
    This prevents overloading the queue with the same action multiple times.
    :param trigger_id:
    :return:
    """
    return ActionQueue.objects.filter(
        trigger_id=trigger_id,
        endedAt__isnull=True,
    ).order_by('createdAt').last()


#TODO: move to settings or into the ping script? could be a trigger value?
MAX_PING_TIME_MINUTES = 2
PING_RETRY_DELAY_SECONDS = 5


async def cancel_whole_action_chain(queue_entry: ActionQueue):
    pending_actions = await get_pending_actions()
    entries = []
    next_entry = next((x for x in pending_actions if x.dependsOn == queue_entry), None)
    while next_entry is not None:
        # build the list in reverse, to cancel the last entry first, so nothing that depends on something else could
        # accidentally get started in the middle of this operation!
        entries.insert(0, next_entry)
        next_entry = next((x for x in pending_actions if x.dependsOn == next_entry), None)

    end = now()
    for entry in entries:
        # all entries end at the same time
        entry.endedAt = end
        await entry.asave()
        await async_safe_log('error', f"Prior action failed, whole action chain cancelled.", extra={'action_id': entry.action.id})

    queue_entry.endedAt = end
    await queue_entry.asave()


async def run_ping_action(queue_entry: ActionQueue, script_class: TypedScript):
    while True:
        result: bool = await script_class.run(queue_entry.value)
        if result:
            queue_entry.endedAt = now()
            await async_safe_log('info', f"Executed successfully", extra={'action_id': queue_entry.action.id})
            await queue_entry.asave()
            break
        else:
            if queue_entry.startedAt + timedelta(minutes=MAX_PING_TIME_MINUTES) < now():
                await async_safe_log('error', f"Ping timed out, execution cancelled.",
                                     extra={'action_id': queue_entry.action.id})
                await cancel_whole_action_chain(queue_entry)

        await asyncio.sleep(PING_RETRY_DELAY_SECONDS)


async def run_action(queue_entry: ActionQueue, script_class: TypedScript):
    try:
        # Execute the action
        await script_class.run(queue_entry.value)

        # Set endedAt with the given maximum duration of the action
        queue_entry.endedAt = now() + timedelta(seconds=queue_entry.action.maximumDurationSeconds or 0)
        await queue_entry.asave()
    except Exception as e:
        await async_safe_log('error', str(e), extra={'action_id': queue_entry.action.id})
        await cancel_whole_action_chain(queue_entry)


process_tasks = set()


@sync_to_async
def get_pending_actions() -> [ActionQueue]:
    # all these select related are required, because they have to get fetches right here and not later inside the async code
    return list(ActionQueue.objects.filter(endedAt__isnull=True).order_by('createdAt').select_related('action', 'trigger', 'action__hardware', 'dependsOn').all())


@sync_to_async
def get_last_entry_by_hardware(hardware: Hardware) -> ActionQueue:
    return ActionQueue.objects.filter(
        action__hardware=hardware,
        endedAt__isnull=False,
    ).order_by('-endedAt').first()


@sync_to_async
def get_last_manual_action_by_hardware(hardware: Hardware, exclude: ActionQueue) -> ActionQueue:
    return ActionQueue.objects.filter(
        action__hardware=hardware,
        trigger__type='manual',
        endedAt__isnull=False,
    ).exclude(
        id=exclude.id
    ).select_related('action').order_by('createdAt').last()


async def process_action_queue():
    """
    Iterates through all the not finished triggers and processes them (checks if the trigger still triggers and if the
    action is executable)

    :return:
    """
    while True:
        # Filter out finished and cancelled actions
        try:
            pending_actions = await get_pending_actions()
            for queue_entry in pending_actions:
                action = queue_entry.action
                trigger = queue_entry.trigger
                hardware = action.hardware

                # Don't execute actions for inactive controllable action
                if not action.isActive:
                    await async_safe_log('debug' ,f"Skipping action because it is not active.", extra={'action_id':action.id})
                    continue

                # Don't execute if the action is still waiting on another actions execution
                if queue_entry.dependsOn is not None and (queue_entry.dependsOn.endedAt is None or queue_entry.dependsOn.endedAt > now()):
                    await async_safe_log('debug', f"Skipping entry because it is still waiting on its predecessor.", extra={'action_id': action.id})
                    continue

                # Don't execute auto actions if manual action is active, cancel the auto action in the queue
                # New auto action would need to be triggered again
                if trigger.type != 'manual' and not action.isAutomated:
                    await async_safe_log('info', f"Cancel execution, because action is set to manual.", extra={'action_id':action.id})
                    queue_entry.endedAt = now()
                    queue_entry.asave()
                    continue

                if hardware is not None:
                    # Don't execute if another action for the same hardware is still running
                    last_entry = await get_last_entry_by_hardware(hardware)
                    if last_entry and last_entry.endedAt > now():
                        await async_safe_log('debug', f"Skipping execution, hardware {hardware} is busy until {last_entry.endedAt}", extra={'action_id':action.id})
                        continue

                    # Don't execute if other actions with the same hardware are on manual mode while this one is on auto.
                    manual_entry = await get_last_manual_action_by_hardware(hardware, queue_entry)
                    # No other active manual action for the same hardware when the action is in manual mode
                    # when this action is in auto mode
                    if manual_entry and not manual_entry.action.isAutomated and action.isAutomated:
                        await async_safe_log('debug', f"Skipping execution, hardware {hardware} has another action in MANUAL mode, which is blocking this auto trigger.", extra={'action_id':action.id})
                        continue

                script = typed_action_script_factory.get_typed_action_script_class(str(action.actionClassId))
                script_class = script(action)

                # Setting startedAt and endedAt right here.
                # OVERESTIMATING the endedAt time here leniently so none of the next process_queue calls will react to it before it being truly finished
                # only after the task has finished later, setting the actual real end time.
                # But we do have to set it here so we don't run into any cases where we check for ended_at is null
                # and double process the entry, that could be bad.
                queue_entry.startedAt = now()
                if script_class.get_script_type() == ScriptType.PING:
                    queue_entry.endedAt = now() + timedelta(minutes=MAX_PING_TIME_MINUTES + 1)
                    await queue_entry.asave()
                    task = asyncio.create_task(run_ping_action(queue_entry, script_class))
                else:
                    queue_entry.endedAt = now() + timedelta(seconds=action.maximumDurationSeconds + 1 or 1)
                    await queue_entry.asave()
                    task = asyncio.create_task(run_action(queue_entry, script_class))

                process_tasks.add(task)
                task.add_done_callback(process_tasks.discard)
        except Exception as e:
            await async_safe_log('error', str(e), extra={'fpf_id': await async_get_fpf_id()})
        await asyncio.sleep(1)


def run_process_queue_in_thread():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_action_queue())
    except Exception as e:
        logger.error(e)


def create_auto_triggered_actions_in_queue(action_id=None):
    auto_triggers = get_all_active_auto_triggers(action_id)
    for auto_trigger in auto_triggers:
        handler = TriggerHandlerFactory.get_handler(auto_trigger)
        handler.enqueue_if_needed()


def is_new_action(action_id, trigger_id):
    """
    Returns if the given trigger id is a new one for the controllable action (or for the hardware) or not.
    We call this function to prevent spamming the queue with the same action multiple times.
    :return:
    """
    if get_action_by_id(action_id).hardware is not None:
        active_state = get_active_state_of_hardware(get_action_by_id(action_id).hardware.id)
    else:
        active_state = get_active_state_of_action(action_id)
    if active_state is None or active_state.trigger.id != trigger_id:
        return True
    return False


def get_action_queue_for_fpf() -> ActionQueueSerializerDescriptive:
    queue = ActionQueue.objects.all()
    return ActionQueueSerializerDescriptive(queue, many=True)


def clear_action_queue():
    ActionQueue.objects.filter(endedAt__isnull=True).all().delete()