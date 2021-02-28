from flask import Blueprint

from CTFd.models import Challenges, Flags, db
from CTFd.plugins.flags import FlagException, get_flag_class
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.plugins.migrations import upgrade
from CTFd.utils.user import get_current_user

# do not forget to change challenge_type also in assets/create.html
challenge_type = "personal"

class IndividualFlag(Flags):
    __mapper_args__ = {"polymorphic_identity": "individual"}
    id = db.Column(
        db.Integer, db.ForeignKey("flags.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))

    def __init__(self, *args, **kwargs):
        super(IndividualFlag, self).__init__(**kwargs)
        self.initial = kwargs

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
    challenge_model = Challenges

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
        # submission = request.form or request.get_json()
        flags = IndividualFlag.query.filter_by(challenge_id=challenge.id).all()
        if submission.content_type != "application/json":
            submission = submission.form
        else:
            submission = submission.get_json()
        submission["user_id"] = get_current_user().id
        if len(flags) == 0:
            return False, "There are no flags added to this challenge."
        for flag in flags:
            try:
                result = get_flag_class(flag.type).compare(flag, submission)
                if result == 0:
                    return True, "Correct"
                elif result > 0 :
                    return False, "You have cheated from user : " + str(result) + " !!!"
            except FlagException as e:
                return False, e.message

        return False, "Incorrect!"




def load(app):
    upgrade()
    CHALLENGE_CLASSES[challenge_type] = PersonalValueChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/" + challenge_type + "_challenges/assets/"
    )
