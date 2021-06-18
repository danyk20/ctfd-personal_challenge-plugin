import os, sys, inspect, argparse, random

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
path = os.path.dirname(current_dir).split("/")[:-3]
parent_dir = "/".join(str(x) for x in path)
sys.path.insert(0, parent_dir)
os.chdir(parent_dir)

from CTFd import create_app
from CTFd.cache import cache
from CTFd.models import (Challenges, Users, Admins, Configs, Pages)
from CTFd.plugins.personal_challenges import IndividualFlag
from CTFd.utils import config, get_config, set_config
from CTFd.utils.uploads import get_uploader, upload_file
from CTFd.utils.email import (
    DEFAULT_PASSWORD_RESET_BODY,
    DEFAULT_PASSWORD_RESET_SUBJECT,
    DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
    DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
    DEFAULT_USER_CREATION_EMAIL_BODY,
    DEFAULT_USER_CREATION_EMAIL_SUBJECT,
    DEFAULT_VERIFICATION_EMAIL_BODY,
    DEFAULT_VERIFICATION_EMAIL_SUBJECT,
)
from sqlalchemy.exc import IntegrityError

app = create_app()
INPUT_ARG = None

names = ["Daniel", "Peter", "John", "Ela", "Lili", "Ron", "Harry", "Jack", "Kevin", "Alis", "Bob", "Alice", "Mat",
         "Jan", "Isabel", "Vachen", "Dima", "Leo", "Raulf", "Sara", "Casto", "Jui", "Sam"]


def setup():
    if not config.is_setup():
        with app.app_context():
            # General
            ctf_name = "Kypo game session"
            ctf_description = "Demo test game"
            user_mode = "users"
            set_config("ctf_name", ctf_name)
            set_config("ctf_description", ctf_description)
            set_config("user_mode", user_mode)

            # Style
            ctf_logo = None
            if ctf_logo:
                f = upload_file(file=ctf_logo)
                set_config("ctf_logo", f.location)

            ctf_small_icon = None
            if ctf_small_icon:
                f = upload_file(file=ctf_small_icon)
                set_config("ctf_small_icon", f.location)

            theme = "core"
            set_config("ctf_theme", theme)
            theme_color = "black"
            theme_header = get_config("theme_header")
            if theme_color and bool(theme_header) is False:
                # Uses {{ and }} to insert curly braces while using the format method
                css = (
                    '<style id="theme-color">\n'
                    ":root {{--theme-color: {theme_color};}}\n"
                    ".navbar{{background-color: var(--theme-color) !important;}}\n"
                    ".jumbotron{{background-color: var(--theme-color) !important;}}\n"
                    "</style>\n"
                ).format(theme_color=theme_color)
                set_config("theme_header", css)

            # DateTime
            start = ""
            end = None
            set_config("start", start)
            set_config("end", end)
            set_config("freeze", None)

            # Administration
            print("Creating initial admin")

            name = "admin"
            email = "admin@muni.cz"
            password = "admin"

            admin = Admins(
                name=name, email=email, password=password, type="admin", hidden=True
            )

            # Create an empty index page
            page = Pages(title=None, route="index", content="", draft=False)

            # Splice in our banner
            index = f"""<div class="row">
                                    <div class="col-md-6 offset-md-3">
                                        <img class="w-100 mx-auto d-block" style="max-width: 500px;padding: 50px;padding-top: 14vh;" src="/themes/core/static/img/logo.png?d=70fce07a" />
                                        <h3 class="text-center">
                                            <p>A cool CTF platform from <a href="https://ctfd.io">ctfd.io</a></p>
                                            <p>Follow us on social media:</p>
                                            <a href="https://twitter.com/ctfdio"><i class="fab fa-twitter fa-2x" aria-hidden="true"></i></a>&nbsp;
                                            <a href="https://facebook.com/ctfdio"><i class="fab fa-facebook fa-2x" aria-hidden="true"></i></a>&nbsp;
                                            <a href="https://github.com/ctfd"><i class="fab fa-github fa-2x" aria-hidden="true"></i></a>
                                        </h3>
                                        <br>
                                        <h4 class="text-center">
                                            <a href="admin">Click here</a> to login and setup your CTF
                                        </h4>
                                    </div>
                                </div>"""
            page.content = index

            # Visibility
            set_config("challenge_visibility", "private")
            set_config("registration_visibility", "public")
            set_config("score_visibility", "public")
            set_config("account_visibility", "public")

            # Verify emails
            set_config("verify_emails", None)
            set_config("mail_server", None)
            set_config("mail_port", None)
            set_config("mail_tls", None)
            set_config("mail_ssl", None)
            set_config("mail_username", None)
            set_config("mail_password", None)
            set_config("mail_useauth", None)

            # Set up default emails
            set_config("verification_email_subject", DEFAULT_VERIFICATION_EMAIL_SUBJECT)
            set_config("verification_email_body", DEFAULT_VERIFICATION_EMAIL_BODY)

            set_config(
                "successful_registration_email_subject",
                DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
            )
            set_config(
                "successful_registration_email_body",
                DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
            )

            set_config(
                "user_creation_email_subject", DEFAULT_USER_CREATION_EMAIL_SUBJECT
            )
            set_config("user_creation_email_body", DEFAULT_USER_CREATION_EMAIL_BODY)

            set_config("password_reset_subject", DEFAULT_PASSWORD_RESET_SUBJECT)
            set_config("password_reset_body", DEFAULT_PASSWORD_RESET_BODY)

            set_config(
                "password_change_alert_subject",
                "Password Change Confirmation for {ctf_name}",
            )
            set_config(
                "password_change_alert_body",
                (
                    "Your password for {ctf_name} has been changed.\n\n"
                    "If you didn't request a password change you can reset your password here: {url}"
                ),
            )
            set_config("setup", True)

            db = app.db
            try:
                db.session.add(admin)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

            try:
                db.session.add(page)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

            db.session.close()
            cache.clear()


def create_individual_flag(player_id=1, challenge_id=1):
    with app.app_context():
        db = app.db
        f = IndividualFlag(
            user_id=player_id,
            challenge_id=challenge_id,
            content=names[player_id % len(names)] + str(challenge_id),
            type="individual",
            data="case_sensitive"
        )
        db.session.add(f)
        db.session.commit()
        db.session.close()


def create_challenge(id=1):
    with app.app_context():
        db = app.db
        chal = Challenges(
            name="Test Challenge" + str(id),
            description="It is working",
            value=100 + id,
            category="MUNI",
            type="personal"
        )
        db.session.add(chal)
        db.session.flush()
        id = chal.id
        db.session.commit()
        db.session.close()
        return id


def create_admin():
    with app.app_context():
        db = app.db
        adm = Admins(
            name="admin",
            password="admin",
            email="admin" + str(random.randint(0, 10000)) + "@muni.cz",
        )
        db.session.add(adm)
        db.session.flush()
        id = adm.id
        db.session.commit()
        db.session.close()
        return id


def create_player(id=1):
    with app.app_context():
        db = app.db
        pl = Users(
            name=names[id % len(names)],
            password="password",
            email=names[id % len(names)] + str(random.randint(0, 100000)) + "@muni.cz",
        )
        db.session.add(pl)
        db.session.flush()
        id = pl.id
        db.session.commit()
        db.session.close()
        return id


def parse_input():
    my_parser = argparse.ArgumentParser()
    my_parser.version = '1.0'
    my_parser.add_argument('-c', '--challenges', action='store', help='number of challenges to be added into database',
                           default="10")
    my_parser.add_argument('-p', '--players', action='store', help='number of players to be added into database',
                           default="10")
    my_parser.add_argument('-f', '--flags', action='store_true', help="add an individual flag for each user and each challenge")
    global INPUT_ARG
    input_arg = my_parser.parse_args()


def generate():
    print("Initializing setup...")
    setup()
    players_id = []
    challenges_id = []
    for p in range(int(INPUT_ARG.players)):
        print("Generating player " + str(p))
        players_id.append(create_player(p))
    for c in range(int(INPUT_ARG.challenges)):
        print("Generating challenge " + str(c))
        challenges_id.append(create_challenge(c))
        if INPUT_ARG.flags:
            for p in range(int(INPUT_ARG.players)):
                print("Generating flag for player " + str(p) + " in challenge " + str(c))
                create_individual_flag(players_id[p], challenges_id[c])

parse_input()

if __name__ == "__main__":
    generate()
