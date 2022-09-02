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


from firebase_admin import credentials, initialize_app, storage
# Init firebase with your credentials
cred = credentials.Certificate("firebaseServiceAccount.json")
initialize_app(cred, {'storageBucket': 'incarto-43f1e.appspot.com'})

# Put your local file path 
fileName = "image.jpg"
bucket = storage.bucket()
blob = bucket.blob('Enhanced/'+fileName)
blob.upload_from_filename(fileName)

# Opt : if you want to make public access from the URL
blob.make_public()

print("your file url", blob.public_url)