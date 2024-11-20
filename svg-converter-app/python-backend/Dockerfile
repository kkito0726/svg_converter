FROM python:3.12

WORKDIR /usr/src/server

COPY . .

RUN mkdir static && apt-get update \
 && apt-get install -y fontconfig \
 && pip install --upgrade pip \
 && pip install -r requirements.txt

 CMD [ "python", "app.py" ]