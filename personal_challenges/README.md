# Personal Challenges for CTFd

This CTFd plugin creates a possibility to create individual flag for each player.

Within CTFd you are free to mix and match regular, dynamic and personal challenges .

The current implementation works only with individual flags!

Individual Flags can be created by APG app https://gitlab.fi.muni.cz/kypolab/theses/apg/kosc-automated-problem-generation-app .


# Tests

0. Open cmd from running docker image of ctfd_ctfd_1.
1. Run database insertion test run `$ python3 CTFd/plugins/personal_challenges/tests/populate.py`
