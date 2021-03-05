# CTFd Personal Challenge plugin
---
---
Plugin to give CTFd the ability to work with individual flags which are included.

Individual flag creates unique flag for each user which brings many advantages.

## Prerequisites
---
---
1. Download CTFd using the command `$ git clone https://github.com/CTFd/CTFd.git`
2. Checkout the correct version 3.2.1 `git checkout tags/3.2.1`

## Installation
---
---
### Linux (Ubuntu/Debian)
---

1. Clone the project with `$ git clone https://gitlab.fi.muni.cz/kypolab/theses/apg/ctfd-personal_challenge-plugin.git`
2. Navigate to directory where CTFd is stored `$ cd <path>`
3. Add 2 lines of code with  `$ echo "from CTFd.plugins.loader import loader_namespace\nCTFd_API_v1.add_namespace(loader_namespace, \"/loader\") " >> CTFd/CTFd/api/__init__.py `
4. Copy downloaded plugin into CTFd `$ cp -a CTFd-personal_challenge-plugin/. CTFd/CTFd/plugins/`


## Usage
---
---
After the installation simply run the command `$ docker-compose up` in CTFd directory to run CTFd server.

Or simply run the command `$ docker-compose -f /<absolut_path>/CTFd/docker-compose.yml up` to launch CTFd server.

Create game and you will be able to add Personal Challenges that use generated values from Kosc-automated-problem-generation-app. 