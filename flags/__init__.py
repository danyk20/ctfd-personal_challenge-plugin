import re
import sys

from CTFd.plugins import register_plugin_assets_directory


class FlagException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class BaseFlag(object):
    name = None
    templates = {}

    @staticmethod
    def compare(self, saved, provided):
        return True

class CTFdIndividualFlag(BaseFlag):
    name = "individual"
    templates = {  # Nunjucks templates used for key editing & viewing
        "create": "/plugins/flags/assets/individual/create.html",
        "update": "/plugins/flags/assets/individual/edit.html",
    }

    @staticmethod
    def compare(chal_key_obj, provided):
        user_id = provided.get("user_id") # id of player who entered flag
        if user_id is None:
            sys.stderr.write("User id value is missing! \n You have probably forgotten to add `request_data[\"user_id\"] = str(session[\"id\"])` on line 464 in ctfd/api/v1/challenges.py . ")
            return -1
        flag = provided["submission"] # entered flag by user
        saved = chal_key_obj.content # flag saved in database
        data = chal_key_obj.data # case_insensitive or case_sensitive
        owner = chal_key_obj.user_id # this particular flag belongs to

        # is flag correct
        if len(saved) != len(flag):
            return -1
        result = 0
        if data == "case_insensitive":
            for x, y in zip(saved.lower(), flag.lower()):
                result |= ord(x) ^ ord(y)
        else:
            for x, y in zip(saved, flag):
                result |= ord(x) ^ ord(y)
        if result == 0:
            # is it player's flag
            if owner == int(user_id):
                return 0
            else:
                # cheated from owner
                return owner
        return -1


class CTFdStaticFlag(BaseFlag):
    name = "static"
    templates = {  # Nunjucks templates used for key editing & viewing
        "create": "/plugins/flags/assets/static/create.html",
        "update": "/plugins/flags/assets/static/edit.html",
    }

    @staticmethod
    def compare(chal_key_obj, provided):
        saved = chal_key_obj.content
        data = chal_key_obj.data

        if len(saved) != len(provided):
            return False
        result = 0

        if data == "case_insensitive":
            for x, y in zip(saved.lower(), provided.lower()):
                result |= ord(x) ^ ord(y)
        else:
            for x, y in zip(saved, provided):
                result |= ord(x) ^ ord(y)
        return result == 0


class CTFdRegexFlag(BaseFlag):
    name = "regex"
    templates = {  # Nunjucks templates used for key editing & viewing
        "create": "/plugins/flags/assets/regex/create.html",
        "update": "/plugins/flags/assets/regex/edit.html",
    }

    @staticmethod
    def compare(chal_key_obj, provided):
        saved = chal_key_obj.content
        data = chal_key_obj.data

        try:
            if data == "case_insensitive":
                res = re.match(saved, provided, re.IGNORECASE)
            else:
                res = re.match(saved, provided)
        # TODO: this needs plugin improvements. See #1425.
        except re.error as e:
            raise FlagException("Regex parse error occured") from e

        return res and res.group() == provided


FLAG_CLASSES = {"static": CTFdStaticFlag, "regex": CTFdRegexFlag,  "individual": CTFdIndividualFlag}


def get_flag_class(class_id):
    cls = FLAG_CLASSES.get(class_id)
    if cls is None:
        raise KeyError
    return cls


def load(app):
    register_plugin_assets_directory(app, base_path="/plugins/flags/assets/")
