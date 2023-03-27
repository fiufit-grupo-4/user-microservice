# set py 3.10 as base image to Docker Engine
FROM python:3.10

# create working dir for image and container
WORKDIR /app

# copy FastAPI app framework and dependencies into working dir
COPY requirements.txt .

RUN pip install -r requirements.txt

# copy rest of the files and source code from the host to the app container working directory
COPY . .

# expose FastAPI app on specific port inside the container
EXPOSE $SERVICE_PORT

# command to start and run FastAPI app container
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "2222"]