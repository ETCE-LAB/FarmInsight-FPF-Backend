from django.core.management.base import BaseCommand
import platform
import subprocess
import os

class Command(BaseCommand):
    help = "Install and configure Mosquitto MQTT broker"

    def handle(self, *args, **options):
        system = platform.system()
        base_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts")
        base_path = os.path.abspath(base_path)

        if system == "Windows":
            script = os.path.join(base_path, "install_mosquitto_windows.bat")
        elif system == "Darwin":
            script = os.path.join(base_path, "install_mosquitto_mac.sh")
        else:
            script = os.path.join(base_path, "install_mosquitto_linux.sh")

        self.stdout.write(f"Running install script for OS: {system}")
        self.stdout.write(f"Script path: {script}")

        if not os.path.exists(script):
            self.stderr.write(f"❌ Script not found: {script}")
            return

        if system == "Windows":
            result = subprocess.run(["wscript", "django_server\\scripts\\install_mosquitto_launcher.vbs"])
            #result = subprocess.run(
            #    ["cmd.exe", "/c", script],
            #    capture_output=True,
            #    text=True,
            #    encoding="utf-8",  # or try "latin1" or "cp1252" if utf-8 still fails
            #)
        else:
            result = subprocess.run(["bash", script], capture_output=True, text=True)

        if result.stdout:
            self.stdout.write("=== STDOUT ===")
            self.stdout.write(result.stdout)

        if result.stderr:
            self.stdout.write("=== STDERR ===")
            self.stderr.write(result.stderr)

        if result.returncode != 0:
            self.stderr.write(result.stderr)
            self.stderr.write("❌ Script execution failed.")
        else:
            self.stdout.write("✅ Script executed successfully.")