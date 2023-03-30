## Base Microservices Infrastructure

[![codecov](https://codecov.io/gh/fiufit-grupo-4/base-microservice/branch/develop/graph/badge.svg?token=TYSBTIXP4G)](https://codecov.io/gh/fiufit-grupo-4/base-microservice) [![Dev Checks](https://github.com/fiufit-grupo-4/base-microservice/actions/workflows/dev-checks.yml/badge.svg)](https://github.com/fiufit-grupo-4/base-microservice/actions/workflows/dev-checks.yml)

### Docker

Build container:

```$ docker-compose build```

Start services:

```$ docker-compose up```

List images:

```$ docker images```

Remove multiple images:

```$ docker rmi <...> -f```

### Dependencies

After any change in *pyproject.toml* file (always execute this before installing):

```$ poetry lock```

Install Poetry for DEV:

```$ poetry install -E dev```

Install Poetry for PROD:

```$ poetry install```

### Tests

Run tests:

```$ poetry run pytest tests```

Format check:

```$ poetry run flake8 --max-line-length=88 app```

Auto-format:

```$ poetry run black --skip-string-normalization app```
