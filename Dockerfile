FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update -y && apt -y install python3.9 python3-pip cmake libgl1-mesa-glx libgtk2.0-dev wget

RUN pip3 install --upgrade pip

RUN pip3 install Flask

RUN pip3 install opencv-python

RUN mkdir trafficlight

COPY . /trafficlight

RUN cd /trafficlight && wget -O /trafficlight/yolov3.weights http://download.louissoft.kr/yolov3.weights

CMD cd /trafficlight && python3 /trafficlight/main.py