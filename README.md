# CTFd Personal Challenge plugin
---
---
Plugin to give CTFd the ability to work with individual flags which are included.

Individual flag creates unique flag for each user which brings many advantages.

## Prerequisites
---
---
1. Download CTFd using the command `$ git clone -b '3.2.1' --single-branch https://github.com/CTFd/CTFd.git`


## Installation
---
---
### Linux (Ubuntu/Debian)
---

1. Navigate into CTFd directory `$ cd <path>/CTFd`
2. Clone the project with `$ git clone https://gitlab.fi.muni.cz/kypolab/theses/apg/ctfd-personal_challenge-plugin.git`
3. Copy downloaded plugin into CTFd `$ cp -R -L -f ctfd-personal_challenge-plugin/* CTFd/plugins/ && rm -rf ctfd-personal_challenge-plugin`


## Usage
---
---
After the installation simply run the command `$ docker-compose up` in CTFd directory to run CTFd server.

Or simply run the command `$ docker-compose -f /<absolut_path>/CTFd/docker-compose.yml up` to launch CTFd server.

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

![view](https://gitlab.fi.muni.cz/kypolab/theses/apg/ctfd-personal_challenge-plugin/-/blob/master/screenshots/admin_panel.png)
![view](https://gitlab.fi.muni.cz/kypolab/theses/apg/ctfd-personal_challenge-plugin/-/blob/master/screenshots/admin_panel.png)
![view](https://gitlab.fi.muni.cz/kypolab/theses/apg/ctfd-personal_challenge-plugin/-/blob/master/screenshots/challenges.png)
![view](https://gitlab.fi.muni.cz/kypolab/theses/apg/ctfd-personal_challenge-plugin/-/blob/master/screenshots/create_challenge.png)
![view](https://gitlab.fi.muni.cz/kypolab/theses/apg/ctfd-personal_challenge-plugin/-/blob/master/screenshots/personal.png)
![view](https://gitlab.fi.muni.cz/kypolab/theses/apg/ctfd-personal_challenge-plugin/-/blob/master/screenshots/visible.png)
![view](https://gitlab.fi.muni.cz/kypolab/theses/apg/ctfd-personal_challenge-plugin/-/blob/master/screenshots/done.png)

