FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

ENV BOT_TOKEN=NTk1MzYzMzkyODg2MTQ1MDQ2.XYWagw.-oVpbLyZ6EFwRGzYHzAujeTpICc

ENV FUNCTIONS_LINK=https://us-central1-bitchbot-discordbot.cloudfunctions.net

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./core.py" ]
