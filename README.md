## Base Microservices Infrastructure

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

Run tests:

```$ poetry pytest tests/```

Format check:

```poetry run flake8 --max-line-length=88 app```

Auto-format:

```poetry run black --skip-string-normalization app```
