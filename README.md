## Base Microservices Infrastructure

[![codecov](https://codecov.io/gh/fiufit-grupo-4/base-microservice/branch/develop/graph/badge.svg?token=TYSBTIXP4G)](https://codecov.io/gh/fiufit-grupo-4/base-microservice) 
[![Tests & Linters](https://github.com/fiufit-grupo-4/base-microservice/actions/workflows/checks.yml/badge.svg?branch=develop)](https://github.com/fiufit-grupo-4/base-microservice/actions/workflows/checks.yml)

### Docker

Build container:

```$ docker-compose build```

Start services:

```$ docker-compose up```

List images:

```$ docker images```

Remove multiple images:

```$ docker rmi <...> -f```

### Tests

After any change in *pyproject.toml* file:

```$ poetry lock```

Install Poetry:

```$ poetry install```

Run tests:

```$ poetry pytest tests/```

Format check:

```$ poetry run flake8 --max-line-length=88 app```

Auto-format:

```$ poetry run black --skip-string-normalization app```
