FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

ENV GOOGLE_APPLICATION_CREDENTIALS=service_account.json
ENV JISHAKU_NO_DM_TRACEBACK=true
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./core.py" ]
