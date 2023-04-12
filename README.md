## User Microservice

[![codecov](https://codecov.io/gh/fiufit-grupo-4/user-microservice/branch/main/graph/badge.svg?token=PG668CYNXE)](https://codecov.io/gh/fiufit-grupo-4/user-microservice) [![Dev Checks](https://github.com/fiufit-grupo-4/user-microservice/actions/workflows/dev-checks.yml/badge.svg)](https://github.com/fiufit-grupo-4/user-microservice/actions/workflows/dev-checks.yml)

# Docker

### Build container:

```$ docker-compose build```

### Start services:

```$ docker-compose up```

### List images:

```$ docker images```

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

### Install Poetry for DEVELOPMENT:

```$ poetry install -E dev```

### Install Poetry for PRODUCTION:

```$ poetry install```

# Tests

### Run tests with pytest for unit tests (TDD)

```$ poetry run pytest tests```

### Run tests with Cucumber (BDD)

```$ poetry run behave tests/features```

### Format check:

```$ poetry run flake8 --max-line-length=88 app```

### Auto-format:

```$ poetry run black --skip-string-normalization app```
