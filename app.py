from flask import Flask, render_template, request, redirect, url_for
import cv2
import os

app = Flask(__name__)

# Directory to save captured images
IMAGE_DIR = 'static/images'
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Route to capture image
@app.route('/capture', methods=['POST'])
def capture_image():
    # Initialize the camera
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    
    if ret:
        # Save the captured image
        image_path = os.path.join(IMAGE_DIR, 'captured_image.jpg')
        cv2.imwrite(image_path, frame)
    
    camera.release()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)