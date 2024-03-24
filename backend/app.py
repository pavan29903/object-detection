import cv2 as cv
import numpy as np
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

config_file = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
frozen_model = 'frozen_inference_graph.pb'
label_file = 'labels.txt'

model = cv.dnn_DetectionModel(frozen_model, config_file)
classLabels = []
with open(label_file, 'rt') as fpt:
    classLabels = fpt.read().rstrip('\n').split('\n')
model.setInputSize(320, 320)
model.setInputScale(1.0/127.5)
model.setInputMean((127.5,127.5,127.5))
model.setInputSwapRB(True)

def detect_and_render_objects(image):

    ClassIndex, confidence, bbox = model.detect(image, confThreshold=0.4)
    
    filtered_detections = []
    for index, conf, boxes in zip(ClassIndex.flatten(), confidence.flatten(), bbox):
        label = classLabels[index-1]
        if label in ['car', 'motorbike', 'bus']:
            filtered_detections.append({'class': label, 'confidence': float(conf), 'bbox': boxes.tolist()})
    
    font_scale = 0.5
    font = cv.FONT_HERSHEY_SIMPLEX
    for detection in filtered_detections:
        boxes = detection['bbox']
        label = detection['class']
        conf = detection['confidence']
        cv.rectangle(image, boxes, (0, 233, 0), 2)
        cv.putText(image, label, (boxes[0]+10, boxes[1]-10), font, fontScale=font_scale, color=(0, 0, 255), thickness=2)
    
    return image, filtered_detections 


@app.route('/', methods=['POST'])
def object_detection():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    npimg = np.fromstring(file.read(), np.uint8)
    uploaded_image = cv.imdecode(npimg, cv.IMREAD_COLOR)
    
    rendered_image = uploaded_image.copy()
    
    
    rendered_image, filtered_detections = detect_and_render_objects(rendered_image)
    

    _, encoded_rendered_image = cv.imencode('.jpg', rendered_image)
    encoded_rendered_image_str = base64.b64encode(encoded_rendered_image).decode('utf-8')
    
  
    _, encoded_uploaded_image = cv.imencode('.jpg', uploaded_image)
    encoded_uploaded_image_str = base64.b64encode(encoded_uploaded_image).decode('utf-8')

    detection_results = {
        'cars': sum(1 for detection in filtered_detections if detection['class'] == 'car'),
        'buses': sum(1 for detection in filtered_detections if detection['class'] == 'bus'),
        'motorbikes': sum(1 for detection in filtered_detections if detection['class'] == 'motorbike')
    }
    
    
    return jsonify({'rendered_image': encoded_rendered_image_str, 'uploaded_image': encoded_uploaded_image_str, 'detection_results': detection_results})

if __name__ == '__main__':
    app.run(debug=True, port=5009)

