# set py 3.9.16 as base image to Docker Engine! 
# Slim-buster is a lightweight version for server deployment
FROM python:3.9.16-slim-buster

RUN pip install poetry

# create working dir for image
WORKDIR /app

# copy dependancies from host to container
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
ENV POETRY_VIRTUALENVS_IN_PROJECT true
RUN poetry install

# expose FastAPI app on specific port inside the container
EXPOSE ${PORT}

# copy app from host to container
ADD app/ app/

# command to start and run FastAPI app container
CMD exec poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port ${PORT}