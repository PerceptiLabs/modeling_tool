from mixpanel import Mixpanel
import os
import logging
import datetime
import functools

from perceptilabs.settings import MIXPANEL_TOKEN_DEV, MIXPANEL_TOKEN_PROD
from perceptilabs.utils import is_pytest, is_dev

logger = logging.getLogger(__name__)

_DEFAULT_TOKEN = MIXPANEL_TOKEN_DEV if is_dev() else MIXPANEL_TOKEN_PROD
_TOKEN = os.getenv("PL_MIXPANEL_TOKEN", _DEFAULT_TOKEN)


def _is_valid_json(obj):
    import json

    try:
        json.dumps(obj)
    except:
        return False
    else:
        return True


class EventTracker:
    def __init__(self, raise_errors=False):
        self._mp = Mixpanel(_TOKEN)
        self._raise_errors = raise_errors

    def emit(self, event_name, call_context, properties):
        try:
            self._set_user_meta(call_context)
            properties = self._prepare_properties(call_context, properties)
            self._send_event(call_context, event_name, properties)
        except:
            if is_dev():
                logger.exception("Event might not have been sent!")

            if self._raise_errors:
                raise

    def _send_event(self, call_context, event_name, properties):
        self._assert_enabled()

        distinct_id = call_context.user_unique_id
        if not distinct_id:
            raise ValueError("Neither email nor id have been given.")
        self._mp.track(
            distinct_id=distinct_id, event_name=event_name, properties=properties
        )

        if is_dev():
            logger.info(f"Event {event_name} sent!")

    def _user_dict(self, call_context, email_key, id_key):
        ret = {}
        user_email = call_context.get("user_email")
        if user_email:
            ret[email_key] = user_email

        user_id = call_context.get("user_id")
        if user_id:
            ret[id_key] = user_id

        return ret

    def _set_user_meta(self, call_context):
        current_time = datetime.datetime.utcnow()
        try:
            distinct_id = call_context.user_unique_id
            user_props = self._user_dict(call_context, "$email", "$user_id")
            self._mp.people_set_once(distinct_id, {"$created": current_time})
            self._mp.people_set(
                distinct_id, {**user_props, "$last_login": current_time}
            )
        except:
            if self._raise_errors:
                raise

    def _prepare_properties(self, call_context, properties):
        """Drop invalid args"""
        new_properties = self._user_dict(call_context, "user_email", "user_id")
        for key, value in properties.items():
            if _is_valid_json(value):
                new_properties[key] = value
            else:
                if is_dev():
                    logger.error(
                        f"Value of argument '{key}' is not json serializable. Skipping!"
                    )
                continue

        if _is_valid_json(new_properties):
            return new_properties
        else:
            if is_dev():
                logger.error(
                    f"Properties is not json serializable. No properties will be included!"
                )
            return {}

    def _assert_enabled(self):
        from unittest.mock import MagicMock

        if is_pytest() and not isinstance(self._mp.track, MagicMock):
            raise Exception(
                "Mixpanel.track should NOT be called during pytests unless mocked!"
            )

        if is_pytest() and not isinstance(self._mp.people_set, MagicMock):
            raise Exception(
                "Mixpanel.people_set should NOT be called during pytests unless mocked!"
            )

        if is_pytest() and not isinstance(self._mp.people_set_once, MagicMock):
            raise Exception(
                "Mixpanel.people_set_once should NOT be called during pytests unless mocked!"
            )
