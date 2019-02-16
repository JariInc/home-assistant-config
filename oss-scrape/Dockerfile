FROM python:alpine3.7

RUN apk add --no-cache build-base openssl-dev libffi-dev libxml2-dev libxslt-dev

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-u", "./main.py" ]