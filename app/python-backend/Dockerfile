FROM python:3.12

WORKDIR /usr/src/server

COPY . .

RUN pip install --upgrade pip \
 && pip install -r requirements.txt

CMD [ "python", "app.py" ]
