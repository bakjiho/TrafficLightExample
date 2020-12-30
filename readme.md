# Traffic Light Example
[![Run on Ainize](https://ainize.ai/images/run_on_ainize_button.svg)](https://ainize.web.app/redirect?git_repo=https://github.com/bakjiho/TrafficLightExample)

This project recognize traffic lights at korea.
It uses YOLOv3 and OpenCV libraries with python3.

It takes 7,000 traffic light images and 30,000 training counts.

![testing](https://user-images.githubusercontent.com/6459539/103330330-5a006780-4aa4-11eb-93f6-8a57aa2b5beb.gif)


## Class structure
We used 10 classes. 3balls traffic lights or 4balls traffic lights.

|class number|class name|
|----|----|
|0|3 red|
|1|3 yellow|
|2|3 green|
|3|3 left|
|4|4 red|
|5|4 green|
|6|4 yellow|
|7|4 red left|
|8|4 left green|
|9|4 red yellow|

## How to run
terminal
```
python3 main.py
```
and go url with your browsers.
```
http://localhost/
```
done!

## Result image
![result](https://user-images.githubusercontent.com/6459539/103330379-99c74f00-4aa4-11eb-91ea-507878e788d4.jpg)
