# Personal Challenges for CTFd

This CTFd plugin allows to create individual flag for each player.

Within CTFd you are free to mix and match regular, dynamic and personal challenges .

The current implementation of the personal challenge works if and only if individual flags are used!

Individual flags can be created by APG app https://gitlab.fi.muni.cz/kypolab/theses/apg/kosc-automated-problem-generation-app .

##Usage

Create game and you will be able to add Personal Challenges that use generated values from Kosc-automated-problem-generation-app. 

    0. Login as Admin
    1. Navigate into Admin Panel
    2. Pick Challenges
    3. Click on "Create Challenge" button
    4. Choose Personal type
    5. Fill all fields
    6. Click on "Create" button
    7. Choose state Hidden/Visible
    8. Click "Finish" button
    9. Generate individuals flags using Kosc-automated-problem-generation-app

## Example

![login](/personal_challenges/screenshots/login.png)
![admin_panel](/personal_challengesscreenshots/admin_panel.png)
![challenges](/personal_challenges/screenshots/challenges.png)
![create_challenge](/personal_challenges/screenshots/create_challenge.png)
![personal](/personal_challenges/screenshots/personal.png)
![visible](/personal_challenges/screenshots/visible.png)
![done](/personal_challenges/screenshots/done.png)

## Tests

0. Open cmd from running docker image of `ctfd_ctfd_1`.
1. Run database insertion test `$ python3 CTFd/plugins/personal_challenges/tests/populate_personal.py [--flags] [--players <number_of_players>] [--challenges <number_of_challenges>]`
2. It is possible to log in using credentials username : `admin` password : `admin` on `http://localhost:8000/login`

``populate_personal.py`` is small script to fill database with users, challenges, admin and skip setup with default values to test CTFd funtions

`--flags` option add to database for each player and challenge one individual flag

`--players <number_of_players>` option must contain a positive number otherwise default 10 players will be added to database. 

`--challenges <number_of_challenges>` option must contain a positive number otherwise default 10 challenges will be added to database.

Example: `populate_personal.py --flags --players 16 --challenges 3` 

It adds 16 players, 3 challenges and 48 flags (16 players * 3 challenges) into the database. 



