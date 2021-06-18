import argparse
import os

import requests

input_arg = None

content_num = 1


def add_players_into_db(num_of_players):
    os.system(
        "python3 CTFd/plugins/personal_challenges/tests/populate_personal.py --challenges 0 --players " + str(
            num_of_players))


def add_challenges_into_db(num_of_challenges):
    os.system(
        "python3 CTFd/plugins/personal_challenges/tests/populate_personal.py --players 0 --challenges " + str(
            num_of_challenges))


def add_challenges_players_flags_into_db(num_of_players, num_of_challenges):
    os.system(
        "python3 CTFd/plugins/personal_challenges/tests/populate_personal.py --challenges " + str(
            num_of_challenges) + " --players " + str(num_of_players) + " --flags")


def init_with_admin():
    os.system("python3 CTFd/plugins/personal_challenges/tests/populate_personal.py --players 0 --challenges 0")


def already_uploaded(data):
    global content_num
    content_num += 1
    data[4] = {"user_email": "admin@muni.cz", "flag": "test" + str(content_num), "challenge_id": content_num}
    responds = []
    for d in data:
        responds.append(requests.post(input_arg.url + "/store", data=d).json())

    assert not responds[0]["success"] and responds[0]["uploaded"] and responds[0][
        "message"] == "Flag was already uploaded"
    assert not responds[1]["success"] and not responds[1]["uploaded"] and responds[1][
        "message"] == "User does not exist."
    assert not responds[2]["success"] and not responds[2]["uploaded"] and responds[2][
        "message"] == "User does not exist."
    assert not responds[3]["success"] and not responds[3]["uploaded"] and responds[3][
        "message"] == "User does not exist."
    assert responds[4]["success"] and responds[4]["uploaded"] and responds[4]["Flag_data"][
        "content"] == "test" + str(content_num)


def test():
    global input_arg
    global content_num
    url = input_arg.url
    players = input_arg.players
    challenges = input_arg.challenges
    init_with_admin()
    data_chal_1 = {"user_email": "admin@muni.cz", "flag": "test", "challenge_id": 1}
    data_chal_1_unknown = {"user_email": "unknown@muni.cz", "flag": "test", "challenge_id": 1}
    data_chal_wrong_unknown = {"user_email": "unknown@muni.cz", "flag": "test", "challenge_id": 123456789}
    data_chal_wrong = {"user_email": "unknown@muni.cz", "flag": "test", "challenge_id": 123456789}
    data_chal_new = {"user_email": "admin@muni.cz", "flag": "test" + str(content_num), "challenge_id": content_num}
    data = [data_chal_1, data_chal_1_unknown, data_chal_wrong, data_chal_wrong_unknown, data_chal_new]
    responds = []

    for d in data:
        responds.append(requests.post(url + "/store", data=d).json())

    assert not responds[0]["success"] and not responds[0]["uploaded"] and responds[0]["message"].__contains__(
        "Database Error :")
    assert not responds[1]["success"] and not responds[1]["uploaded"] and responds[1][
        "message"] == "User does not exist."
    assert not responds[2]["success"] and not responds[2]["uploaded"] and responds[2][
        "message"] == "User does not exist."
    assert not responds[3]["success"] and not responds[3]["uploaded"] and responds[3][
        "message"] == "User does not exist."
    assert not responds[4]["success"] and not responds[4]["uploaded"] and responds[4][
        "message"].__contains__("Database Error :")
    print("Successfully returned error message for admin empty database.")

    add_challenges_into_db(1)

    responds = []

    for d in data:
        responds.append(requests.post(url + "/store", data=d).json())

    assert responds[0]["success"] and responds[0]["uploaded"] and responds[0]["Flag_data"]["content"] == "test"
    assert not responds[1]["success"] and not responds[1]["uploaded"] and responds[1][
        "message"] == "User does not exist."
    assert not responds[2]["success"] and not responds[2]["uploaded"] and responds[2][
        "message"] == "User does not exist."
    assert not responds[3]["success"] and not responds[3]["uploaded"] and responds[3][
        "message"] == "User does not exist."
    assert not responds[4]["success"] and responds[4]["uploaded"] and responds[4][
        "message"] == "Flag was already uploaded"
    print("Successfully stored flag for admin empty database.")

    add_challenges_into_db(1)
    already_uploaded(data)

    add_players_into_db(players)
    add_challenges_into_db(1)
    already_uploaded(data)
    print("Successfully stored flag for admin " + str(players) + " players in database.")

    add_challenges_into_db(challenges)
    already_uploaded(data)
    print("Successfully stored flag for admin " + str(players) + " players and " + str(
        challenges) + " challenges in database.")

    add_challenges_players_flags_into_db(players, challenges)
    already_uploaded(data)
    print("Successfully stored flag for admin " + str(2 * int(players)) + " players, " + str(
        2 * int(challenges)) + " challenges and " + str(int(players) * int(challenges)) + " flags in database.")


def parse_input():
    my_parser = argparse.ArgumentParser()
    my_parser.version = '1.0'
    my_parser.add_argument('-u', '--url', action='store', help='url address of CTFd server',
                           default="http://localhost:8000")
    my_parser.add_argument('-p', '--players', action='store', help='number of players to be added into database',
                           default="100")
    my_parser.add_argument('-c', '--challenges', action='store', help="number of challenges to be added into database",
                           default="100")
    global input_arg
    input_arg = my_parser.parse_args()


parse_input()
test()
