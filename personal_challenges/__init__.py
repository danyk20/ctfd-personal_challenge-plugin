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

# do not forget to change challenge_type also in assets/create.html
challenge_type = "personal"


def log(submission, origin, challenge):
    filename = "/var/log/CTFd/cheaters.log"
    if os.path.exists(filename):
        append_write = 'a'
    else:
        append_write = 'w'
    f = open(filename, append_write)
    who = get_user_mail(submission["user_id"])
    from_whom = get_user_mail(origin)
    f.write(
        str(who) + ";" + str(from_whom) + ";" + str(submission["submission"]) + ";" + str(
            challenge) + ";" + str(datetime.datetime.now().strftime("[%d/%m/%Y %H:%M:%S]")) + ";" + get_ip() + ";\n")
    f.close()


def log_recieved_flag(sender_mail, sender_ip, flag, challenge):
    filename = "/var/log/CTFd/uploaded.log"
    string_log = str(sender_mail) + ";" + str(sender_ip) + ";" + str(flag) + ";" + str(
            challenge) + ";" + str(datetime.datetime.now().strftime("[%d/%m/%Y %H:%M:%S]")) + ";\n"
    if os.path.exists(filename):
        append_write = 'a'

        if os.path.exists("/var/log/CTFd/.recent_update_log.log"):
            f = open("/var/log/CTFd/.recent_update_log.log", 'r')
            if f.readline() == string_log:
                f.close()
                return
            f.close()
        f = open("/var/log/CTFd/.recent_update_log.log", 'w')
        f.write(string_log)
        f.close()
    else:
        append_write = 'w'
    f = open(filename, append_write)
    f.write(string_log)
    f.close()


class IndividualFlag(Flags):
    __mapper_args__ = {"polymorphic_identity": "individual"}
    id = db.Column(
        db.Integer, db.ForeignKey("flags.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))

    def __init__(self, *args, **kwargs):
        super(IndividualFlag, self).__init__(**kwargs)
        self.initial = kwargs


class Flag(Flags):
    __mapper_args__ = {"polymorphic_identity": "static"}

    def __init__(self, *args, **kwargs):
        super(Flag, self).__init__(**kwargs)
        self.initial = kwargs


class Flag(Flags):
    __mapper_args__ = {"polymorphic_identity": "regex"}

    def __init__(self, *args, **kwargs):
        super(Flag, self).__init__(**kwargs)
        self.initial = kwargs


class PersonalChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "personal"}

    def __init__(self, *args, **kwargs):
        super(PersonalChallenge, self).__init__(**kwargs)
        self.initial = kwargs["value"]


class PersonalValueChallenge(BaseChallenge):
    id = challenge_type  # Unique identifier used to register challenges
    name = challenge_type  # Name of a challenge type
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        "create": "/plugins/" + challenge_type + "_challenges/assets/create.html",
        "update": "/plugins/" + challenge_type + "_challenges/assets/update.html",
        "view": "/plugins/" + challenge_type + "_challenges/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/" + challenge_type + "_challenges/assets/create.js",
        "update": "/plugins/" + challenge_type + "_challenges/assets/update.js",
        "view": "/plugins/" + challenge_type + "_challenges/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/" + challenge_type + "_challenges/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        challenge_type + "_challenges",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = PersonalChallenge

    @classmethod
    def attempt(cls, challenge, submission):
        """
        This method is used to check whether a given input is right or wrong. It does not make any changes and should
        return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param challenge: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()
        temp = []
        correct_flag = False
        flag_owners = []

        for i in range(len(flags)):
            if flags[i].type == "individual":
                res = IndividualFlag.query.filter_by(id=flags[i].id).first()
                if res:
                    temp.append(res)
                else:
                    Flags.query.filter_by(id=flags[i].id).delete()

        flags = temp
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
                    else:
                        continue
                result = get_flag_class(flag.type).compare(flag, submission)
                if result == 0:
                    correct_flag = True
                if result > 0:
                    flag_owners.append(result)
            except FlagException as e:
                return False, e.message

        for owner in flag_owners:
            log(submission, owner, challenge.id)
        if correct_flag:
                return True, "Correct"
        return False, "Incorrect!"


def init_store():

    challenge_id = str(request.form.get('challenge_id'))
    flag = str(request.form.get('flag'))
    user_email = str(request.form.get('user_email'))
    user_id = get_user_id(user_email)
    user_ip = request.remote_addr

    log_recieved_flag(user_email, user_ip, flag, challenge_id)

    if user_id == 0:
        return {"success": False, "message": "User does not exist.", "uploaded": False}

    flags_list = IndividualFlag.query.filter_by(user_id = user_id).all()
    for f in flags_list:
        if f and Flags.query.filter_by(id = f.id).first().challenge_id == int(challenge_id):
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
        f = FlagModel(**req)
        db.session.add(f)
        db.session.commit()
        db.session.close()


    except Exception as e:
        return {"success": False, "message": "Database Error :" + str(e), "uploaded": False}

    return {"success": True, "Flag_data": req, "uploaded": True}


def get_user_id(mail):
    user = Users.query.filter_by(email=mail).first()
    if user:
        return user.id
    else:
        return 0


def get_user_mail(id):
    user = Users.query.filter_by(id=id).first()
    return user.email


def get_flag(flag_id):
    if request.method != 'GET':
        return old_flag_get(flag_id)
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
        return old_flag_get(flag_id)
    return {"success": True, "data": response.data}


def load(app):
    upgrade()
    CHALLENGE_CLASSES[challenge_type] = PersonalValueChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/" + challenge_type + "_challenges/assets/"
    )

    global old_flag_get
    old_flag_get = app.view_functions['api.flags_flag']
    app.view_functions['api.flags_flag'] = get_flag

    @app.route('/store', methods=['POST'])
    @bypass_csrf_protection
    def store():
        return init_store()
