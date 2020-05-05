FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt ./

EXPOSE 6969

ENV JISHAKU_NO_DM_TRACEBACK=true
ENV OAUTHLIB_INSECURE_TRANSPORT=true

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./core.py" ]
