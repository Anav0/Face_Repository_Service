import os
import face_recognition
from flask import Flask, jsonify, request, redirect,send_file,render_template
from pymongo import MongoClient
from flask import json
from bson.json_util import dumps
from bson import ObjectId
from flask_cors import CORS

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
CORS(app)
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

@app.route('/worker', methods=['POST'])
def PostWorker():
#fullname, hourlyWage, overtimeHourlyWage, email, phone, postion, department

    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'photo' not in request.files:
            return json.dumps({'success':False}), 404, {'ContentType':'application/json'}
        file = request.files['photo']

        if file.filename == '':
            return json.dumps({'success':False}), 404, {'ContentType':'application/json'}
        print(request.form)
        if file and allowed_file(file.filename):
                fullname=request.form['fullname']
                hourlyWage=float(request.form['hourlyWage'])
                overtimeHourlyWage=float(request.form['overtimeHourlyWage'])
                email=request.form['email']
                phone=request.form['phone']
                position = request.form['position']
                department=request.form['department']
                img = face_recognition.load_image_file(file)
                unknown_face_encodings = face_recognition.face_encodings(img)

                collection.insert_one({"fullname":fullname,
                "hourlyWage":hourlyWage,
                "overtimeHourlyWage":overtimeHourlyWage,
                "email":email,
                "phone":phone,
                "position":position,
                "department":department,
                "value":str(unknown_face_encodings[0])})
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        else:
                return json.dumps({'success':False}), 404, {'ContentType':'application/json'}
    else:
         return json.dumps({'success':False}), 404, {'ContentType':'application/json'}
@app.route('/worker', methods=["GET"])
def GetPerson():
    return dumps(collection.find())

@app.route('/worker/<id>', methods=["GET"])
def GetPersonById(id):
    return dumps(collection.find_one({'_id': ObjectId(id)}))

@app.route('/worker', methods=["PUT"])
def UpdateWorker():
    #try:
        #photo = request.files["photo"]
    #except:
        #return json.dumps({'success': False, 'message': "Invalid arguments"}), 400, {'ContentType': 'application/json'}

    if request.form["_id"] is None:
        return json.dumps({'success': False, 'message': "Lack of required parameters"}), 400, {'ContentType': 'application/json'}

    collection.update_one({'_id': ObjectId(request.form["_id"])},
                                        {'$set':{
                                       'fullname': request.form["fullname"],
                                        'hourlyWage': float(request.form["hourlyWage"]),
                                        'overtimeHourlyWage': float(request.form['overtimeHourlyWage']),
                                        'email': request.form['email'],
                                        'phone': request.form['phone'],
                                        'position': request.form['position'],
                                        'department': request.form['department']
                                        }})

    return dumps(collection.find_one({'_id': ObjectId(request.form['_id'])}))

@app.route('/rcp', methods=["POST"])
def PostRCP():
    try:
        employee_id = request.args.get("employee_id")
        time_stamp = int(request.args.get("time_stamp"))
        action = request.args.get("action")
    except:
        return json.dumps({'success':False, 'message':"Invalid arguments"}), 400, {'ContentType':'application/json'}

    if employee_id is None or time_stamp is None or action is None:
        return json.dumps({'success':False, 'message':"Lack of required parameters"}), 400, {'ContentType':'application/json'}

    rcp = {
        "employee_id": ObjectId(employee_id),
        "time_stamp": time_stamp,
        "action": action,
    }
    rcp_collection.insert_one(rcp)

    return dumps(rcp), 200, {'ContentType':'application/json'}

@app.route('/rcp', methods=["PATCH"])
def UpdateRCP():
    try:
        rcp =  request.files["rcp"]
        print(rcp)
    except:
        return json.dumps({'success':False, 'message':"Invalid arguments"}), 400, {'ContentType':'application/json'}

    if rcp["_id"] is None:
        return json.dumps({'success':False, 'message':"Lack of required parameters"}), 400, {'ContentType':'application/json'}

    return dumps(rcp_collection.update_one({'_id':id},{'action':rcp["action"],'time_stamp':rcp["time_stamp"],'employee_id':rcp["employee_id"]})), 200, {'ContentType':'application/json'}

@app.route('/rcp', methods=["GET"])
def GetRCP():
    employee_id = request.args.get("employee_id")
    rcp_id = request.args.get("rcp_id")

    if employee_id is not None:
        result = rcp_collection.find({"employee_id":ObjectId(employee_id)})
        return dumps(result)
    if rcp_id is not None:
       result = rcp_collection.find_one({"_id":ObjectId(rcp_id)})
       return dumps(result)
    if rcp_id is None and employee_id is None:
       result = rcp_collection.find()
       return dumps(result)
    if result is None:
       return json.dumps({'success':False,'message':"No RCP record found"}), 404, {'ContentType':'application/json'}
    return dumps(result)


@app.route('/rcp/range', methods=["GET"])
def GetRCPRange():
    try:
        employee_id = request.args.get("employee_id")
        startDate = int(request.args.get("startDate"))
        endDate = int(request.args.get("endDate"))
        print(startDate, endDate)
    except:
       return json.dumps({'success':False,'message':"Invalid arguments"}), 400, {'ContentType':'application/json'}
    result = None
    if employee_id and startDate and endDate:
        result=rcp_collection.find({'employee_id':ObjectId(employee_id),'time_stamp':{"$lte":endDate, "$gte":startDate}})
        return dumps(result)
    if startDate and endDate:
       # 1554069600000 # 01.04.2019 <- start date
       # 1556661600000 # 01.05.19 <- time stamp
       # 1557056746403 # <- end date :c
        result=rcp_collection.find({'time_stamp':{"$gte":startDate,"$lte":endDate }})
        return dumps(result)

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


    Name="undefined"
    id="undefined"
    #Check if exist such value
    #values=collection.distinct("value")
    values=collection.find({})
    for faces in values:

        #Convert string to float list
                 print(faces)
                 helplist=[]
                 pureList=[]
                 helplist=CleanDataFromDB(faces["value"]).split(' ')
                 for point in range(len(helplist)):
                     if helplist[point] is not '':
                        pureList.append(float(helplist[point]))
                #Compare faces from Database and photo
                 try: 
                     if ComparingFaces(pureList,unknown_face_encodings[0])[0]:
                #Add path to photos to list
                       record=collection.find_one({"value":faces["value"]})
                       Name=faces["fullname"]
                       id=faces["_id"]
                 except:
                     Name="undefined"
                     id="undefined"   

    # Return the result as json{"value":values[faces]}

    result = {
        "name":Name,
        "_id":str(id)
    }
   # print(RequireName)
      #  if faceExist:
    #else:
    return jsonify(result)
if __name__ == "__main__":
    app.run(host='192.168.1.101', port=5001, debug=True)
