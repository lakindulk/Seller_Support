  # imports
import os
from unittest import result
#from util import base64_to_pil
from tensorflow.keras.preprocessing import image
import cv2
from PIL import Image
import requests
from keras.models import Sequential,model_from_json
import numpy as np
import uuid
from flask_cors import CORS

#firebase imports
from firebase_admin import credentials, initialize_app, storage

# Flask
from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect

config = {
    "apiKey": "AIzaSyDR1tatcOFWjn7pojBALC2X8BbJlvlNDXU",
    "authDomain": "incarto-43f1e.firebaseapp.com",
    "projectId": "incarto-43f1e",
    "storageBucket": "incarto-43f1e.appspot.com",
    "messagingSenderId": "823539441122",
    "appId": "1:823539441122:web:93be675155990ba74c6dbb",
    "measurementId": "G-5V5RX8ZDZ4",
    "databaseURL": "gs://incarto-43f1e.appspot.com",
}


# Init firebase with your credentials
cred = credentials.Certificate("firebaseServiceAccount.json")
initialize_app(cred, {'storageBucket': 'incarto-43f1e.appspot.com'})



# Declare a flask app
app = Flask(__name__)
CORS(app)

def get_ImageClassifierModel():
	json_file = open("EfficientNetB5_model.json", 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	loaded_model = model_from_json(loaded_model_json)
	# load weights into new model
	loaded_model.load_weights("EfficientNetB5_model.h5")

	return loaded_model
	# print("Loaded model from disk")

model=get_ImageClassifierModel()	

def predict_class(class_index):
	if(class_index==0):
		return 'Backyard'
	elif(class_index==1):
		return 'Bathroom'
	elif(class_index==2):
		return 'Bedroom'
	elif(class_index==3):
		return 'DinningRoom'
	elif(class_index==4):
		return 'Frontyard'
	elif(class_index==5):
		return 'Kitchen'
	else:
		return 'Living Room'
    


def model_predict(url):

	'''
	Prediction Function for model.
	Arguments: 
	img: is address to image
	model : image classification model
	'''
	im = Image.open(requests.get(url, stream=True).raw)
	img = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
	img_orginal = cv2.resize(img,(224,224),cv2.IMREAD_UNCHANGED)
	# plt.imshow(img)
	resized_img = image.img_to_array(img_orginal)
	final_image= np.expand_dims(resized_img, axis=0)

	# loaded_model = get_ImageClassifierModel()
	predictions =model.predict(final_image)
	return predict_class(np.argmax(predictions))

def enhance_image(imgUrl):
	img = Image.open(requests.get(imgUrl, stream=True).raw)

	img = Image.open(requests.get(imgUrl, stream=True).raw)

	R, G, B = cv2.split(np.array(img))

	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

	output_R = clahe.apply(R)
	output_G = clahe.apply(G)
	output_B = clahe.apply(B)
	#plt.imshow(output)

	output = cv2.merge((output_R, output_G, output_B))
	fileDir = os.path.dirname(os.path.realpath('__file__'))
	file_path = os.path.join(fileDir, 'EnhancedImages/')
	# file_path = "EnhancedImages/"
	filename = uuid.uuid4().hex+".jpg"
	cv2.imwrite(file_path+filename, cv2.cvtColor(output, cv2.COLOR_RGB2BGR))

	return file_path+filename, filename
	# return filename



@app.route('/')
def index():
    return jsonify("Welcome to InCarto")
	
@app.route('/predict', methods=['GET', 'POST'])
def predict():
	'''
	predict function to predict the image
	'''
	if request.method == 'POST':
		# Get the image from post request
		#img = base64_to_pil(request.json)
		url = request.json.get('url')
		# initialize model
		# print(url)

		# Make prediction
		result = model_predict(url)


		# Serialize the result, you can add additional fields
		return jsonify(result=result)
	return None

@app.route('/enhanceImage', methods=['GET', 'POST'])
def upload_enhanced_image():

	if request.method == 'POST': 
		# url = 'https://firebasestorage.googleapis.com/v0/b/incarto-43f1e.appspot.com/o/fitted%20(2).jpg?alt=media&token=a170081f-a6a3-45da-bbb0-c93a884445d9'
		# url = request.args.get('url')
		url = request.json.get('url')
		# print(url)

		file_path, filename = enhance_image(url)
		# filename = enhance_image(url)

		bucket = storage.bucket()
		blob = bucket.blob('Enhanced/'+ filename)
		blob.upload_from_filename(file_path)

		# Opt : if you want to make public access from the URL
		blob.make_public()

		print("your file url", blob.public_url)
		return jsonify(result=blob.public_url)
	return None

if __name__ == '__main__':
	app.run(debug=True,port = 5001)