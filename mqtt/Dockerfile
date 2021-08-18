FROM python:3.8-slim

ARG TMP=tmptmptmp

RUN echo ${TMP}

# Create app directory
WORKDIR /app

# Install app dependencies
COPY requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY . /app

EXPOSE 9101
CMD [ "python", "mqtt.py" ]