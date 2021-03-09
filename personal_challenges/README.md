# Personal Challenges for CTFd

This CTFd plugin allows to create individual flag for each player.

Within CTFd you are free to mix and match regular, dynamic and personal challenges .

The current implementation of the personal challenge works if and only if individual flags are used!

Individual flags can be created by APG app https://gitlab.fi.muni.cz/kypolab/theses/apg/kosc-automated-problem-generation-app .


# Tests

0. Open cmd from running docker image of `ctfd_ctfd_1`.
1. Run database insertion test `$ python3 CTFd/plugins/personal_challenges/tests/populate.py [--flags]`
2. It is possible to log in using credentials username : `admin` password : `admin` on `http://localhost:8000/login`

``populate.py`` is small script to fill database with users, challenges, admin and skip setup with default values to test CTFd funtions

`--flags` option add to database for each player and challenge one individual flag



