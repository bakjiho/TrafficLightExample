# -*- coding: utf-8 -*-
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

def findimg(imgpath, resultpath):
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    classes = []
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    # get image
    img = cv2.imread(imgpath, cv2.IMREAD_COLOR)

    height, width, channels = img.shape

    # Detecting objects
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL)

    net.setInput(blob)

    outs = net.forward(output_layers)

    # display info
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # 좌표
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = colors[i]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label, (x, y + 30), font, 1.5, color, 2)
    # outt.write(img)
    cv2.imwrite(resultpath, img)

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/result')
def result_page():
    return render_template('result.html')

@app.route('/fileUpload', methods=['GET', 'POST'])
def upload_file():
    if request.method =='POST':
        f = request.files['file']
        f.save('static/upload/' + secure_filename(f.filename))
        findimg('static/upload/' + secure_filename(f.filename), 'static/results/' + secure_filename(f.filename))
        return redirect(url_for('result_page', secure=secure_filename(f.filename)))

@app.route('/api/fileUpload', methods=['GET', 'POST'])
def upload_api():
    if request.method =='POST':
        f = request.files['file']
        f.save('static/upload/' + secure_filename(f.filename))
        findimg('static/upload/' + secure_filename(f.filename), 'static/results/' + secure_filename(f.filename))
        return 'static/results/' + secure_filename(f.filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

