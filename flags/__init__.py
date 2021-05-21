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
    """
    A class to represent a individual flag logic.
    ...

        Attributes
        ----------
        name : String
            flag type name

        templates : dict
            Nunjucks templates used for key editing & viewing

        Methods
        -------
        compare(chal_key_obj, provided):
            Method to check if submitted flag is correct.
    """
    name = "individual"
    templates = {
        "create": "/plugins/flags/assets/individual/create.html",
        "update": "/plugins/flags/assets/individual/edit.html",
    }

    @staticmethod
    def compare(chal_key_obj, provided):
        """
                Static method to check if submitted flag is correct.

                Parameters
                    ----------
                    chal_key_obj : Flag
                        row from database

                    provided : dict
                        submission data

                Returns
                    -------
                    int
                        flag owner ID if was submitted shared flag,
                        if the flag is correct 0 otherwise -1

        """
        submitter_id = provided.get("user_id")
        if submitter_id is None:
            sys.stderr.write(
                "ID of player who submitted flag is missing! Cannot check the flag!")
            return -1
        submitted_flag = provided["submission"]
        saved_flag = chal_key_obj.content
        case_sensitivity = chal_key_obj.data
        flag_owner = chal_key_obj.user_id

        # is flag correct
        if len(saved_flag) != len(submitted_flag):
            return -1
        result = 0
        if case_sensitivity == "case_insensitive":
            submitted_flag = submitted_flag.lower()
        for x, y in zip(saved_flag, submitted_flag):
            result |= ord(x) ^ ord(y)
        if result == 0:
            # is it player's flag
            if flag_owner == int(submitter_id):
                return 0
            # cheated from owner
            return flag_owner
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


FLAG_CLASSES = {"static": CTFdStaticFlag, "regex": CTFdRegexFlag, "individual": CTFdIndividualFlag}


def get_flag_class(class_id):
    cls = FLAG_CLASSES.get(class_id)
    if cls is None:
        raise KeyError
    return cls


def load(app):
    register_plugin_assets_directory(app, base_path="/plugins/flags/assets/")
