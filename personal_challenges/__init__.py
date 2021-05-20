import json
import os
import datetime

from flask import Blueprint, request

from CTFd.models import Challenges, Flags, db, Users
from CTFd.plugins.flags import FlagException, get_flag_class
from CTFd.plugins import register_plugin_assets_directory, bypass_csrf_protection
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.plugins.migrations import upgrade
from CTFd.utils.user import get_current_user
from CTFd.schemas.flags import FlagSchema
from CTFd.utils.user import get_ip

CHALLENGE_TYPE = "personal"
OLD_FLAG_GETTER = None


def log(submission, origin, challenge):
    """
        Function to log suspicious activity that may reveal cheating.

            Parameters
                ----------
                submission : dict
                    submission data

                origin : int
                    player ID

                challenge : int
                    challenge ID

            Returns
                -------
                None
    """
    filename = "/var/log/CTFd/" + PersonalValueChallenge.cheaters_log_file + ".log"
    with open(filename, 'a') as file:
        who = get_user_mail(submission["user_id"])
        from_whom = get_user_mail(origin)
        file.write(str(who) + ";" + str(from_whom) + ";" + str(submission["submission"]) + ";"
            + str(challenge) + ";" + str(datetime.datetime.now().strftime("[%d/%m/%Y %H:%M:%S]"))
            + ";" + get_ip() + ";\n")


def log_received_flag(sender_mail, sender_ip, flag, challenge):
    """
        Function to log received flags post request trying to upload flag.

            Parameters
                ----------
                sender_mail : String
                    Email address of player who sent post request

                sender_ip : String
                    IP address of player who sent post request

                flag : int
                    flag content

                challenge : int
                    challenge ID

            Returns
                -------
                None
    """
    string_log = str(sender_mail) + ";" + str(sender_ip) + ";" \
                 + str(flag) + ";" + str(challenge) + ";" \
                 + str(datetime.datetime.now().strftime("[%d/%m/%Y %H:%M:%S]")) + ";\n"

    if os.path.isfile("/var/log/CTFd/.recent_" + PersonalValueChallenge.upload_log_file
                      + "_log.log"):
        with open("/var/log/CTFd/.recent_" + PersonalValueChallenge.upload_log_file
                  + "_log.log", 'r') as last_log:
            if last_log.readline() == string_log:
                return
    with open("/var/log/CTFd/.recent_" + PersonalValueChallenge.upload_log_file
              + "_log.log", 'w') as last_log:
        last_log.write(string_log)
    with open("/var/log/CTFd/" + PersonalValueChallenge.upload_log_file + ".log", 'a') as log_file:
        log_file.write(string_log)


class IndividualFlag(Flags):
    """
        A class to represent a individual flag model in database.
        ...

            Attributes
            ----------
            __mapper_args__ : dict
                what type of flag is this class for

            id : int
            flag ID

            user_id : int
            owner ID

            Methods
            -------


    """
    __mapper_args__ = {"polymorphic_identity": "individual"}
    id = db.Column(
        db.Integer, db.ForeignKey("flags.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial = kwargs


class Flag(Flags):
    """
        A class to represent a static flag model in database.
        ...

            Attributes
            ----------
            __mapper_args__ : dict
                what type of flag is this class for

            Methods
            -------
    """
    __mapper_args__ = {"polymorphic_identity": "static"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial = kwargs


class Flag(Flags):
    """
        A class to represent a regex flag model in database.
        ...

            Attributes
            ----------
            __mapper_args__ : dict
                what type of flag is this class for

            Methods
            -------
    """
    __mapper_args__ = {"polymorphic_identity": "regex"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial = kwargs


class PersonalChallenge(Challenges):
    """
        A class to represent a personal challenges model in database.
        ...

            Attributes
            ----------
            __mapper_args__ : dict
                what type of flag is this class for

            Methods
            -------
    """
    __mapper_args__ = {"polymorphic_identity": "personal"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial = kwargs["value"]


class PersonalValueChallenge(BaseChallenge):
    """
        A class to represent a personal challenges model in database.
        ...

            Attributes
            ----------
            id : String
                Unique identifier used to register challenges

            name : String
                Name of a challenge type

            templates : dict
                Handlebars templates used for each aspect of challenge editing & viewing

            scripts : dict
                Scripts that are loaded when a template is loaded

            route : String
                Route at which files are accessible. This must be registered using
                register_plugin_assets_directory()

            blueprint : Blueprint
                blueprint used to access the static_folder directory

            challenge_model : PersonalValueChallenge
                reference on class type

            cheaters_log_file : String
                name of log file containing potential cheaters players

            upload_log_file : String
                name of log file containing all attempts to upload flag

            Methods
            -------
    """
    id = CHALLENGE_TYPE
    name = CHALLENGE_TYPE
    templates = {
        "create": "/plugins/" + CHALLENGE_TYPE + "_challenges/assets/create.html",
        "update": "/plugins/" + CHALLENGE_TYPE + "_challenges/assets/update.html",
        "view": "/plugins/" + CHALLENGE_TYPE + "_challenges/assets/view.html",
    }
    scripts = {
        "create": "/plugins/" + CHALLENGE_TYPE + "_challenges/assets/create.js",
        "update": "/plugins/" + CHALLENGE_TYPE + "_challenges/assets/update.js",
        "view": "/plugins/" + CHALLENGE_TYPE + "_challenges/assets/view.js",
    }
    route = "/plugins/" + CHALLENGE_TYPE + "_challenges/assets/"
    blueprint = Blueprint(
        CHALLENGE_TYPE + "_challenges",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = PersonalChallenge

    cheaters_log_file = "cheaters"
    upload_log_file = "uploaded"

    @staticmethod
    def clean_individual_flags(flags):
        """
        This static method remove partly deleted flags from database and return only complete ones.
        ...
             Parameters
                ----------
                flags : list
                    list of flags from database

            Returns
                -------
                list
                    list of complete flags
        """
        complete_flags = []
        for current_flag in flags:
            if current_flag.type == "individual":
                res = IndividualFlag.query.filter_by(id=current_flag.id).first()
                if res:
                    complete_flags.append(res)
                else:
                    Flags.query.filter_by(id=current_flag.id).delete()
        return complete_flags

    @classmethod
    def attempt(cls, challenge, submission):
        """
        This method is used to check whether a given input is right or wrong.
        It does not make any changes and should return a boolean for correctness
        and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.
        ...
             Parameters
                ----------
                challenge : Challenge
                    The Challenge object from the database
                submission : request
                    The submitted request by player

            Returns
                -------
                (boolean, String)
                    (is flag correct, message to show)
        """
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()
        correct_flag = False
        flag_owners = []
        flags = cls.clean_individual_flags(flags)
        db.session.commit()

        if submission.content_type != "application/json":
            submission = submission.form
        else:
            submission = submission.get_json()
        submission["user_id"] = get_current_user().id
        if len(flags) == 0:
            return False, "There are no flags added to this challenge."
        for flag in flags:
            try:
                if flag.type != "individual":
                    if get_flag_class(flag.type).compare(flag, submission["submission"]):
                        return True, "Correct"
                    continue
                result = get_flag_class(flag.type).compare(flag, submission)
                if result == 0:
                    correct_flag = True
                if result > 0:
                    flag_owners.append(result)
            except FlagException as err:
                return False, err.message

        for owner in flag_owners:
            log(submission, owner, challenge.id)
        if correct_flag:
            return True, "Correct"
        return False, "Incorrect!"


def init_store():
    """
        Function to initialize the store listener.

             Parameters
                ----------

            Returns
                -------
                dict
                   request response
    """
    challenge_id = str(request.form.get('challenge_id'))
    flag = str(request.form.get('flag'))
    user_email = str(request.form.get('user_email'))
    user_id = get_user_id(user_email)
    user_ip = request.remote_addr

    log_received_flag(user_email, user_ip, flag, challenge_id)

    if not user_id:
        return {"success": False, "message": "User does not exist.", "uploaded": False}

    flags_list = IndividualFlag.query.filter_by(user_id=user_id).all()
    for current_flag in flags_list:
        if current_flag and Flags.query.filter_by(id=current_flag.id).first().challenge_id \
                == int(challenge_id):
            return {"success": False, "message": "Flag was already uploaded", "uploaded": True}

    req = json.loads("{}")
    req["challenge_id"] = challenge_id
    req["content"] = flag
    req["data"] = "Case Sensitive"
    req["type"] = "individual"
    req["user_id"] = user_id

    try:
        # fill IndividualFlags and Flags table
        FlagModel = IndividualFlag
        flag_model = FlagModel(**req)
        db.session.add(flag_model)
        db.session.commit()
        db.session.close()


    except Exception as err:
        return {"success": False, "message": "Database Error :" + str(err), "uploaded": False}

    return {"success": True, "Flag_data": req, "uploaded": True}


def get_user_id(mail):
    """
        Function to get user ID from mail.
            Parameters
                ----------
                mail : String
                    email

            Returns
                -------
                int :
                    user ID


    """
    user = Users.query.filter_by(email=mail).first()
    if user:
        return user.id
    return 0


def get_user_mail(user_id):
    """
         Function to get user mail from ID.

            Parameters
                ----------
                user_id : int
                    user ID

            Returns
                -------
                dict
                    String :
                    user email
    """
    user = Users.query.filter_by(id=user_id).first()
    return user.email


def get_flag(flag_id):
    """
        Function to get flag with given ID via request.

            Parameters
                ----------
                flag_id : int
                    flag ID

            Returns
                -------
                dict :
                    request response
    """
    if request.method != 'GET':
        return OLD_FLAG_GETTER(flag_id)
    flag = Flags.query.filter_by(id=flag_id).first_or_404()
    if flag.type == "individual":
        flag = IndividualFlag.query.filter_by(id=flag_id).first_or_404()
    schema = FlagSchema()
    response = schema.dump(flag)

    if response.errors:
        return {"success": False, "errors": response.errors}, 400

    response.data["templates"] = get_flag_class(flag.type).templates
    if flag.type == "individual":
        response.data["user_id"] = str(flag.user_id)
    else:
        return OLD_FLAG_GETTER(flag_id)
    return {"success": True, "data": response.data}


def load(app):
    """
        Function to load this script into app.

            Parameters
                ----------
                app : Flask
                    a CTFd application

            Returns
                -------
                None
    """

    upgrade()
    CHALLENGE_CLASSES[CHALLENGE_TYPE] = PersonalValueChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/" + CHALLENGE_TYPE + "_challenges/assets/"
    )

    global OLD_FLAG_GETTER
    OLD_FLAG_GETTER = app.view_functions['api.flags_flag']
    app.view_functions['api.flags_flag'] = get_flag

    @app.route('/store', methods=['POST'])
    @bypass_csrf_protection
    def store():
        return init_store()
