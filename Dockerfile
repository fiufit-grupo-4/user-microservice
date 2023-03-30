# set py 3.10 as base image to Docker Engine
FROM python:3.10.6

RUN pip install poetry

# create working dir for image and container
WORKDIR /root
ADD app/ app/

# copy dependancies from host to container
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
ENV POETRY_VIRTUALENVS_IN_PROJECT true
RUN poetry install

# expose FastAPI app on specific port inside the container
EXPOSE ${SERVICE_PORT}

# command to start and run FastAPI app container
CMD exec poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port ${SERVICE_PORT}