FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update -y && apt -y install python3.9 python3-pip cmake libgl1-mesa-glx libgtk2.0-dev git

RUN pip3 install --upgrade pip

RUN pip3 install Flask

RUN pip3 install opencv-python

RUN cd / && git clone https://github.com/bakjiho/TrafficLightExample.git

CMD cd /TrafficLightExample && python3 /TrafficLightExample/test.py