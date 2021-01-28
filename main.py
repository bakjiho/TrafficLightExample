# -*- coding: utf-8 -*-
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import hashlib
import uuid
import threading
import time
from queue import Queue, Empty
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# App is behind one proxy that sets the -For and -Host headers.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
requests_queue = Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.1
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]


# request handling
def handle_requests_by_batch():
    try:
        while True:
            requests_batch = []
            while not (len(requests_batch) >= BATCH_SIZE):
                try:
                    requests_batch.append(requests_queue.get(timeout=CHECK_INTERVAL))
                except Empty:
                    continue

            batch_outputs = ['done']

            for request in requests_batch:
                if len(request["input"]) == 1:
                	findimg(request['input'][0][0], request['input'][0][1])
            for request, output in zip(requests_batch, batch_outputs):
                request["output"] = output

    except Exception as e:
        while not requests_queue.empty():
            requests_queue.get()
        print(e)

threading.Thread(target=handle_requests_by_batch).start()


@app.route('/queue-clear')
def queue_debug():
    try:
        requests_queue.queue.clear()
        return 'Clear', 200
    except Exception:
        return jsonify({'message': 'Queue clear error'}), 400


def findimg(imgpath, resultpath):
    global net, classes, layer_names, output_layers
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
    
@app.route('/healthz')
def health_page():
    return 'ok'

@app.route('/result')
def result_page():
    return render_template('result.html')

@app.route('/fileUpload', methods=['GET', 'POST'])
def upload_file():
	if requests_queue.qsize() > BATCH_SIZE:	
		return Response("Too many requests", status=429)
	uuidstr = str(uuid.uuid4())
	try:
		args = []
		if request.method =='POST':
			f = request.files['file']
			f.save('static/upload/' + uuidstr + '.jpg')
			args.append(('static/upload/' + uuidstr + '.jpg', 'static/results/' + uuidstr + '.jpg'))
	except Exception:
		print("Wrong file")
		return Response("fail", status=400)
	req = {
		'input': args
	}
	requests_queue.put(req)

	while 'output' not in req:
		time.sleep(CHECK_INTERVAL)
	return redirect(url_for('result_page', secure=uuidstr + '.jpg'))	


@app.route('/api/fileUpload', methods=['GET', 'POST'])
def upload_api():
	if requests_queue.qsize() > BATCH_SIZE:	
		return Response("Too many requests", status=429)
	uuidstr = str(uuid.uuid4())
	try:
		args = []
		if request.method =='POST':
			f = request.files['file']
			f.save('static/upload/' + uuidstr + '.jpg')
			args.append(('static/upload/' + uuidstr + '.jpg', 'static/results/' + uuidstr + '.jpg'))
	except Exception:
		print("Wrong file")
		return Response("fail", status=400)

	req = {
		'input': args
	}
	requests_queue.put(req)

	while 'output' not in req:
		time.sleep(CHECK_INTERVAL)
	return send_file('static/results/' + uuidstr + '.jpg')

@app.route('/api/locust')
def locust_api():
    if requests_queue.qsize() > BATCH_SIZE: 
        return Response("Too many requests", status=429)
    try:
        args = []
        args.append(('static/upload/example.jpg', 'static/results/example.jpg'))
    except Exception:
        print("Wrong file")
        return Response("fail", status=400)

    req = {
        'input': args
    }
    requests_queue.put(req)

    while 'output' not in req:
        time.sleep(CHECK_INTERVAL)
    return send_file('static/results/example.jpg')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

