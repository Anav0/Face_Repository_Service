import os
import face_recognition
from flask import Flask, jsonify, request, redirect,send_file,render_template
from pymongo import MongoClient
from flask import json
from bson.json_util import dumps
from bson import ObjectId

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client['WorkersFacesDb']
collection = db['Employees']
rcp_collection = db['RCP']

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
            return json.dumps({'success':False}), 404, {'ContentType':'application/json'}
        file = request.files['file']

        if file.filename == '':
            return json.dumps({'success':False}), 404, {'ContentType':'application/json'}

        if file and allowed_file(file.filename):
                name=request.form['Imie']
                surname=request.form['Nazwisko']
                print(name)
                print(surname)
                img = face_recognition.load_image_file(file)
                unknown_face_encodings = face_recognition.face_encodings(img)
                collection.insert({"imie":name,"nazwisko":surname,"value":str(unknown_face_encodings[0])})
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        else:
                return json.dumps({'success':False}), 404, {'ContentType':'application/json'}
    else:
         return json.dumps({'success':False}), 404, {'ContentType':'application/json'}

@app.route('/person', methods=["GET"])
def GetPerson():
    id = request.args.get("id")
    result = None

    if id is not None:
        result = collection.find_one({'_id': ObjectId(id)})
    else:
        result = collection.find()

    if result is None:
        return json.dumps({'success':False,'message':"No employee record found"}), 404, {'ContentType':'application/json'}

    return dumps(result)

@app.route('/rcp', methods=["POST"])
def PostRCP():
    employee_id = request.args.get("employee_id")
    time_stamp = request.args.get("time_stamp")
    action = request.args.get("action")

    print(employee_id,time_stamp,action)

    if employee_id is None or time_stamp is None or action is None:
        return json.dumps({'success':False, 'message':"Lack of required parameters"}), 400, {'ContentType':'application/json'}

    rcp = {
        "employee_id": ObjectId(employee_id),
        "time_stamp": time_stamp,
        "action": action,
    }
    rcp_collection.insert_one(rcp)

    return dumps(rcp), 200, {'ContentType':'application/json'}

@app.route('/rcp', methods=["GET"])
def GetRCP():
    employee_id = request.args.get("employee_id")
    rcp_id = request.args.get("rcp_id")
    result = None

    if employee_id is not None:
        result = rcp_collection.find({"employee_id":ObjectId(employee_id)})

    if rcp_id is not None:
        result = rcp_collection.find_one({"_id":ObjectId(rcp_id)})

    if rcp_id is None and employee_id is None:
        result = rcp_collection.find()

    if result is None:
        return json.dumps({'success':False,'message':"No RCP record found"}), 404, {'ContentType':'application/json'}
    return dumps(result)

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
