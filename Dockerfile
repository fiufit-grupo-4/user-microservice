# set py 3.10 as base image to Docker Engine
FROM python:3.10

RUN pip install poetry

# create working dir for image and container
WORKDIR /root
ADD app/ app/

# copy dependancies from host to container
COPY pyproject.toml ./

# generate dependancies file everytime dependancies are updated
RUN poetry lock

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
ENV POETRY_VIRTUALENVS_IN_PROJECT true
RUN poetry install

# expose FastAPI app on specific port inside the container
EXPOSE ${SERVICE_PORT}

# command to start and run FastAPI app container
CMD exec poetry run uvicorn app.api:app --host 0.0.0.0 --port ${SERVICE_PORT}