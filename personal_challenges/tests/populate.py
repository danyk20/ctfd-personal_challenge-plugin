import random
import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
path = os.path.dirname(current_dir).split("/")[:-3]
parent_dir = "/".join(str(x) for x in path)
sys.path.insert(0, parent_dir)
os.chdir(parent_dir)

from CTFd import create_app
from CTFd.models import (Challenges, Users, Admins, Configs, Pages)
from CTFd.plugins.personal_challenges import IndividualFlag

app = create_app()

players = 10
challenges = 10

names = ["Daniel", "Peter", "John", "Ela", "Lili", "Ron", "Harry", "Jack", "Kevin", "Alis"]

def setup():
    with app.app_context():
        db = app.db
        event_name = Configs(
            key="ctf_name",
            value="Kypo test game session"
        )
        event_description = Configs(
            key="ctf_description",
            value="Test game created in populate.py"
        )
        event_user_mode = Configs(
            key="user_mode",
            value="users"
        )
        event_setup = Configs(
            key="setup",
            value="1"
        )
        db.session.add(event_name)
        db.session.add(event_description)
        db.session.add(event_user_mode)
        db.session.add(event_setup)
        page = Pages(title=None, route="index", content="", draft=False)
        db.session.add(page)
        db.session.commit()
        db.session.close()

def create_individual_flag(player_id=1, challenge_id=1):
    with app.app_context():
        db = app.db
        f = IndividualFlag(
            user_id=player_id + 1,
            challenge_id=challenge_id + 1,
            content=names[player_id] + str(challenge_id),
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
        db.session.commit()
        db.session.close()


def create_admin():
    with app.app_context():
        db = app.db
        adm = Admins(
            name="admin",
            password="admin",
            email="admin@muni.cz" + str(random.randint(0,10000)),
        )
        db.session.add(adm)
        db.session.commit()
        db.session.close()


def create_player(id=1):
    with app.app_context():
        db = app.db
        pl = Users(
            name=names[id],
            password="password",
            email=names[id] + "@muni.cz" + str(random.randint(0,10000)),
        )
        db.session.add(pl)
        db.session.commit()
        db.session.close()


def generate():
    print("Initializing setup...")
    setup()
    print("Generating admin")
    create_admin()
    for p in range(players):
        print("Generating player " + str(p))
        create_player(p)
    for c in range(challenges):
        print("Generating challenge " + str(c))
        create_challenge(c)
        for p in range(players):
            print("Generating flag for player " + str(p) + " in challenge " + str(c))
            create_individual_flag(p, c)

generate()
