FROM python
MAINTAINER yange
COPY requirements.txt /opt/app/tgbotdocker/requirements.txt
COPY thebot.py /opt/app/tgbotdocker/thebot.py
WORKDIR /opt/app/tgbotdocker
RUN pip install pip update
RUN pip install -r requirements.txt
ENV String
CMD ["python","thebot.py"]