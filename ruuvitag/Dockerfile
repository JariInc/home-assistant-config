FROM python:3.8

RUN apt-get update && apt-get install -y \
  build-essential \
  bluez \
  bluez-hcidump \
  sudo

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-u", "./ruuvitag-mqtt-bridge.py" ]