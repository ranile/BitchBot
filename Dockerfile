FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

ENV GOOGLE_APPLICATION_CREDENTIALS=service_account.json

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./core.py" ]
