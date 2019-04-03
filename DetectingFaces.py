import os
import face_recognition
from flask import Flask, jsonify, request, redirect,send_file,render_template
from pymongo import MongoClient
from flask import json
# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client['WorkersFacesDb']
collection = db['Employees']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/check', methods=['GET', 'POST'])
def Check():
    file = request.files['file']
    return DetectFacesinImage(file)

@app.route('/add', methods=['GET', 'POST'])
def upload_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
                img = face_recognition.load_image_file(file)
                unknown_face_encodings = face_recognition.face_encodings(img)
                collection.insert({"_id_akcji":0,"value":str(unknown_face_encodings[0][0])})
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
        else:
                return json.dumps({'success':False}), 404, {'ContentType':'application/json'} 
 
    #Clean data from spaces and other symbols. Preparing for Convert to Float list 
def CleanDataFromDB(datafromdb):
    result=datafromdb.replace('\n','')
    result=result.replace('[','') 
    result=result.replace(']','')
    return result

def ComparingFaces(listFromDb,listFromPhoto):
    match_results = face_recognition.compare_faces([listFromDb], listFromPhoto)
    return match_results

def DetectFacesinImage(file_stream):
    # Load the uploaded image file
    img = face_recognition.load_image_file(file_stream)
        # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img)

    face_found = False
    faceExist = False
    listForImages=[]
    #Check if exist such value 
    values=collection.distinct("value")         
    for faces in range(len(values)):
        #Convert string to float list
                 helplist=[]
                 pureList=[]
                 helplist=CleanDataFromDB(values[faces]).split(' ')
                 for point in range(len(helplist)):
                     if helplist[point] is not '':
                        pureList.append(float(helplist[point])) 
                #Compare faces from Database and photo
                 if ComparingFaces(pureList,unknown_face_encodings[0])[0]:
                #Add path to photos to list
                    record=collection.find_one({"value":values[faces]})
                    print(record)
                    faceExist = True
                    face_found = True                                 
    # Return the result as json{"value":values[faces]}
    
    result = {
        "face_found_in_image": face_found,
        "is_picture_of_obama": faceExist,
        "pictures where we observed faces":listForImages
    }
   # print(RequireName)
  #  if faceExist:
       
    jsonify(result)
    #else:
    return jsonify(result)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
