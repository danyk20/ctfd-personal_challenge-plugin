# CTFd Personal Challenge plugin
---
---
Plugin to give CTFd the ability to work with individual flags which are included.

Individual flag creates one unique flag for each user per challenge, which brings many advantages (e.g. reveal and reduce solution sharing). 

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
3. Copy downloaded plugin into CTFd `$ cp -R -L -f ctfd-personal_challenge-plugin/. CTFd/plugins/ && rm -rf ctfd-personal_challenge-plugin`

## Update

0. Navigate into the CTFd directory `$ cd <path>/CTFd`
1. Navigate into the plugins directory `$ cd CTFd/plugins`
2. Pull new version of the project with `$ git pull`

## Usage
---
---
After the installation, simply run the command `$ docker-compose up` in the CTFd directory to run the CTFd server.

Or simply run the command `$ docker-compose -f /<absolut_path>/CTFd/docker-compose.yml up` to launch the CTFd server.
