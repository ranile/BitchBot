FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

ENV BOT_TOKEN=not pushing token

ENV FUNCTIONS_LINK=https://us-central1-bitchbot-discordbot.cloudfunctions.net

RUN sudo apt-get install python3-dev

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./core.py" ]
