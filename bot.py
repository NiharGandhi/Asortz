import os
from flask import Flask, render_template, request, jsonify, send_from_directory
import cv2
import dlib
import numpy as np

detector = dlib.get_frontal_face_detector()

app = Flask(__name__)

UPLOAD_FOLDER = 'UPLOAD_FOLDER'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == "POST":
        input_fold = request.files['file']
        output_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'output')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        def save(img, name, bbox, output_folder, width=180, height=227):
            x, y, w, h = bbox
            imgCrop = img[y:h, x:w]
            imgCrop = cv2.resize(imgCrop, (width, height))
            cv2.imwrite(os.path.join(output_folder, name + '.jpg'), imgCrop)

        def faces(pics):
            loc = os.path.basename(pics.filename)
            loc = loc.split('.')[0]
            new_output_folder = os.path.join(output_folder, loc)
            if not os.path.exists(new_output_folder):
                os.makedirs(new_output_folder)
            frame = cv2.imdecode(np.frombuffer(
                pics.read(), np.uint8), cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            fit = 50
            for counter, face in enumerate(faces):
                x1, y1 = face.left(), face.top()
                x2, y2 = face.right(), face.bottom()
                save(frame, str(counter), (x1 - fit, y1 - fit,
                     x2 + fit, y2 + fit), new_output_folder)
            frame = cv2.resize(frame, (800, 800))
            return jsonify({'success': True, 'message': 'Faces cropped successfully'})

        return faces(input_fold)


if __name__ == "__main__":
    app.run()
