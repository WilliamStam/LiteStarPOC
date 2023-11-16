# Setting up the server (Ubuntu server 22.04)


Usually the python versions on linux servers are outdated. if you need to update it to the latest (3.12 in this case)
then:

Python - You can follow just about any guide on how to get the latest python

```shell
sudo apt update && apt upgrade -y
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12
```

To install the virtual environment module:

```shell
sudo apt install python3.12-venv
```

Git

```shell
sudo apt install git
```

Supervisor (systemctl alternative)

```
sudo apt install supervisor
```

# Setting up the project to work from a git source

Create your folder (going to use /opt/api here but you can choose where you want it to go).

```shell
mkdir /opt/api
cd /opt/api
```

Setup a git repo remote (`git pull origin <branch>`)

```shell
git init
git remote add origin <path-to-git-repo>
```

pull your files

```
git pull origin <branch>
```