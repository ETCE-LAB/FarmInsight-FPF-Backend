import base64
import logging
import http.client
import uuid
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
from oauth2_provider.models import get_access_token_model
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.utils import get_timezone


log = logging.getLogger("oauth2_provider")

AccessToken = get_access_token_model()
UserModel = get_user_model()

class CustomOAuth2Validator(OAuth2Validator):
    def _get_token_from_authentication_server(
            self, token, introspection_url, introspection_token, introspection_credentials
    ):
        """Use external introspection endpoint to "crack open" the token.
        :param introspection_url: introspection endpoint URL
        :param introspection_token: Bearer token
        :param introspection_credentials: Basic Auth credentials (id,secret)
        :return: :class:`models.AccessToken`

        Some RFC 7662 implementations (including this one) use a Bearer token while others use Basic
        Auth. Depending on the external AS's implementation, provide either the introspection_token
        or the introspection_credentials.

        If the resulting access_token identifies a username (e.g. Authorization Code grant), add
        that user to the UserModel. Also cache the access_token up until its expiry time or a
        configured maximum time.

        """
        MOCK_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjlFREE4MDY3Qzk0ODFBRkU4QjY1QjNGQThBMjZCRTY3IiwidHlwIjoiYXQrand0In0.eyJpc3MiOiJodHRwczovL2RldmVsb3BtZW50LWlzc2UtaWRlbnRpdHlzZXJ2ZXIuYXp1cmV3ZWJzaXRlcy5uZXQiLCJuYmYiOjE3MzQwODA1NzEsImlhdCI6MTczNDA4MDU3MSwiZXhwIjoxNzM0MDg0MTcxLCJhdWQiOiJodHRwczovL2RldmVsb3BtZW50LWlzc2UtaWRlbnRpdHlzZXJ2ZXIuYXp1cmV3ZWJzaXRlcy5uZXQvcmVzb3VyY2VzIiwic2NvcGUiOlsib3BlbmlkIl0sImFtciI6WyJwd2QiXSwiY2xpZW50X2lkIjoiaW50ZXJhY3RpdmUiLCJzdWIiOiIwOWNmOWM2Zi1mYTU2LTRmYjItYjg1Ni1hYTM1OGYzNmNiNjAiLCJhdXRoX3RpbWUiOjE3MzQwNzgyMzcsImlkcCI6ImxvY2FsIiwiZW1haWwiOiJtYXIucGV0ZXJAb3N0ZmFsaWEuZGUiLCJuYW1lIjoibWFyLnBldGVyQG9zdGZhbGlhLmRlIiwiaWQiOiIwOWNmOWM2Zi1mYTU2LTRmYjItYjg1Ni1hYTM1OGYzNmNiNjAiLCJzaWQiOiIyRjk4QkU4RjI0NkNFOUQ2MTI3MTJBMEU5MkI5MzczNCIsImp0aSI6IjM5RTI3QTk1MzVGNDRCNjk0RDdBRUU2ODc4ODZEMjc2In0.Ai4Ccz4R2krFh8ew2F-Fc9ruNyVOqSi0YbdDUIC6nRnN_YeVvsLjviDC_HfD0-n1mgy91ODSlUxBYW0DFevAwaksk6t2USQZfy9lH8AVdzI2pSpfbUqXIWhi7u9JQ16T6_t7i5QzhARgbrfLtk-4j45uijfqNDnJ1_RmLIkDGhHRjGoXJh9neo7I9lFvioSZ-MP3gYOD8uknQGg-WIliqTsiVBmxy-YsBwq_qKG1qotWzavvH76T1jkEzJAom2GrxYfZViV6SFfq_dYqkUWNXylgP4N34ZdSP8Q_yZk2n-cPgqKy4S3MVQwpiv5Nd0xr88IVE9MBBq6TggptD5xG1w'
        if token == MOCK_TOKEN:
            user, _ = UserModel.objects.get_or_create(**{UserModel.USERNAME_FIELD: 'mock-user', UserModel.EMAIL_FIELD: 'mock@mail.com'})

            expires = make_aware(
                datetime.now(), timezone=get_timezone(oauth2_settings.AUTHENTICATION_SERVER_EXP_TIME_ZONE)
            )

            access_token, _created = AccessToken.objects.update_or_create(
                token=token,
                defaults={
                    "user": user,
                    "application": None,
                    "scope": '',
                    "expires": expires,
                },
            )

            return access_token



        headers = None
        if introspection_token:
            headers = {"Authorization": "Bearer {}".format(introspection_token)}
        elif introspection_credentials:
            client_id = introspection_credentials[0].encode("utf-8")
            client_secret = introspection_credentials[1].encode("utf-8")
            basic_auth = base64.b64encode(client_id + b":" + client_secret)
            headers = {"Authorization": "Basic {}".format(basic_auth.decode("utf-8"))}

        try:
            response = requests.post(introspection_url, data={"token": token}, headers=headers)
        except requests.exceptions.RequestException:
            log.exception("Introspection: Failed POST to %r in token lookup", introspection_url)
            return None

        # Log an exception when response from auth server is not successful
        if response.status_code != http.client.OK:
            log.exception(
                "Introspection: Failed to get a valid response "
                "from authentication server. Status code: {}, "
                "Reason: {}.".format(response.status_code, response.reason)
            )
            return None

        try:
            content = response.json()
        except ValueError:
            log.exception("Introspection: Failed to parse response as json")
            return None

        if "active" in content and content["active"] is True:
            if "id" in content:
                if content["id"] != settings.DASHBOARD_BACKEND_USER_ID: # Only Dashboard Backend allowed to post
                    return None
                user, _ = UserModel.objects.get_or_create(**{UserModel.USERNAME_FIELD: content["id"], UserModel.EMAIL_FIELD: content["email"]})
            else:
                user = None

            max_caching_time = datetime.now() + timedelta(
                seconds=oauth2_settings.RESOURCE_SERVER_TOKEN_CACHING_SECONDS
            )

            if "exp" in content:
                expires = datetime.utcfromtimestamp(content["exp"])
                if expires > max_caching_time:
                    expires = max_caching_time
            else:
                expires = max_caching_time

            scope = content.get("scope", "")

            if settings.USE_TZ:
                expires = make_aware(
                    expires, timezone=get_timezone(oauth2_settings.AUTHENTICATION_SERVER_EXP_TIME_ZONE)
                )

            access_token, _created = AccessToken.objects.update_or_create(
                token=token,
                defaults={
                    "user": user,
                    "application": None,
                    "scope": scope,
                    "expires": expires,
                },
            )

            return access_token