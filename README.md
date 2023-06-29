# User Microservice

[![codecov](https://codecov.io/gh/fiufit-grupo-4/user-microservice/branch/main/graph/badge.svg?token=PG668CYNXE)](https://codecov.io/gh/fiufit-grupo-4/user-microservice) [![Dev Checks](https://github.com/fiufit-grupo-4/user-microservice/actions/workflows/dev-checks.yml/badge.svg)](https://github.com/fiufit-grupo-4/user-microservice/actions/workflows/dev-checks.yml)

This microservice is responsible for managing the different types of users in the system. It has the basic CRUD of the users, along with the functionality to follow users, block users as well as approve requests from known trainers. It also has the functionality to login/singup a user with email and password, or with Google. It also implements the notification system through Firebase connection.

# Documentation

The link to the API documentation of this microservice can be found in the corresponding Swagger: [API Documentation - User Microservice](https://user-service-fiufit-v2.herokuapp.com/docs)

# Docker

### Build container:

```$ docker-compose build```

### Start services:

```$ docker-compose up```

### Remove dangling images: 

When you run a ```docker-compose build```, it creates a new image, but it doesn't remove the old one, so you can have a lot of images with the same name but different id. Then, you can remove all of them with the following command:

```$ docker rmi $(docker images -f dangling=true -q) -f```

### Deep Cleaning - Free space on your disk
**Warning**: This will remove all containers, images, volumes and networks not used by at least one container.
Its **recommended** to run this command before ```docker-compose up``` to avoid problems.

```$ docker system prune -a --volumes```

# Dependencies

After any change in *pyproject.toml* file (always execute this before installing):

```$ poetry lock```

### Install Poetry for DEV:

```$ poetry install -E dev```

### Install Poetry for PROD:

```$ poetry install```

# Tests

### Run tests:

```$ poetry run pytest tests```

### Format check:

```$ poetry run flake8 --max-line-length=88 app```

### Auto-format:

```$ poetry run black --skip-string-normalization app```