FROM python:3.8-slim

# Create app directory
WORKDIR /app

# Install app dependencies
COPY src/requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY src /app

EXPOSE 9101
CMD [ "python", "pihole.py" ]