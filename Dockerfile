FROM python:3.10

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y sudo

RUN apt-get install -y x11-apps

RUN pip install --upgrade pip

RUN adduser --disabled-password --gecos '' docker
RUN adduser docker sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER docker

WORKDIR /polling_service
COPY . /polling_service

RUN pip install -r requirements.txt

ENTRYPOINT ["sudo", "python", "main.py"]
