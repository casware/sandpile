# syntax=docker/dockerfile:1
# set base image
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the source files to the working directory
COPY app.py .
COPY cylindrical.py .
COPY main.py .
COPY hourglass.py .
COPY tests.py .
COPY sandpile.py .

# command to run on container start
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]