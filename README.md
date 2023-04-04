
![example workflow](https://github.com/Q35978/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
# YaMDb Project Description


## Description
The Foodgram project is a website where a user can publish recipes,
add them to Favorites, subscribe to other users and download
a list of products needed to prepare selected dishes.

## The project is available via the links:

```
- http://51.250.92.107/
- http://51.250.92.107admin/
- http://51.250.92.107/api/docs/
```

## Administrator Account:

``
- login: review
- mail: review@y.ru
- password: review1234
```

# Setting up required files

``
# DBMS we work with
DB_ENGINE=django.db.backends.postgresql
# Database name
DB_NAME=
# User name to connect to the database
POSTGRES_USER=
# User password
POSTGRES_PASSWORD=
# Container name
DB_HOST=
# DB connection port
DB_PORT=
# Application key (optional)
SECRET_KEY=
``

# Commands not needed to install the application
On Linux, all commands must be executed as an administrator

- Log in to a remote server
- Install docker:
``
sudo apt install docker.io
``
- Install docker-compose:
``
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose -$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
``
- Edit the nginx.conf file (infra/nginx.conf), be sure to enter the server's IP address in server_name
- Transfer docker-compose files.yml, nginx.conf to a remote server:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
``
- build and run containers on the server:
``
docker-compose up -d --build
``
- Create an .env file according to the template suggested above. Be sure to change the values of POSTGRES_USER and POSTGRES_PASSWORD
- To work with Workflow, add environment variables to Secrets GitHub for work:
```
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<postgres database name>
DB_USER=<db user>
DB_PASSWORD=<password>
DB_HOST=<db>
DB_PORT=<5432>
SECRET_KEY=<application key>

DOCKER_PASSWORD=<DockerHub password>
DOCKER_USERNAME=<user name>

USER=<username to connect to the server where the application will be deployed>
HOST=<Server IP>
SSH_KEY=<your SSH key to connect to the remote server>
PASSPHRASE=<passphrase for ssh key>

TELEGRAM_TO=<ID of the chat to which the message will be sent>
TELEGRAM_TOKEN=<your bot's token>
```
- When the assembly was successful, the following steps must be performed (only at the first deployment):
* conduct migrations:
```
docker-compose exec backend python manage.py migrate
```
* Create a superuser for the first login:
```
docker-compose exec backend python manage.py createsuperuser
```
* Fill in the list of ingredients:
``
docker-compose exec backend python manage.py load_ingredients_from_csv
```

# Technology stack
- Python
- Django REST framework
- PostgreSQL
- Gunicorn
- nginx
- Docker
- Git



