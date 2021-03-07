from CTFd import create_app
from CTFd.models import (Challenges, Users, Admins)
from CTFd.plugins.personal_challenges import IndividualFlag

app = create_app()

players = 10
challenges = 10

names = ["Daniel", "Peter", "John", "Ela", "Lili", "Ron", "Harry", "Jack", "Kevin", "Alis"]


def create_individual_flag(player_id=1, challenge_id=1):
    with app.app_context():
        db = app.db
        f = IndividualFlag(
            user_id=player_id,
            challenge_id=challenge_id,
            content="case_sensitive",
            type="individual",
            data=names[id] + str(challenge_id)
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
            email="admin@muni.cz",
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
            email=names[id] + "@muni.cz",
        )
        db.session.add(pl)
        db.session.commit()
        db.session.close()


def generate():
    create_admin()
    for p in range(players):
        create_player(p)
    for c in range(challenges):
        create_challenge(c)
        for p in range(players):
            create_individual_flag(p, c)
