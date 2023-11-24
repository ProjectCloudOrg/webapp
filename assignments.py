from flask import Flask, request, json
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from sqlalchemy_utils import database_exists, create_database
import csv
import uuid
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/assignmentdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
appHeaders = {'access-control-allow-credentials': 'true', 'access-control-allow-headers': 'X-Requested-With,Content-Type,Accept,Origin', 'access-control-allow-methods': '*', 'access-control-allow-origin': '*', 'cache-control': 'no-cache', 'content-enconding': 'gzip', 'content-type': 'application/json;charset=utf-8', 'etag' : 'W/"a9-N/X4JXf/69QQSQ1CLHMNPzj473I"', 'expires': '-1'} 
appHeadersHealthZ = {'cache-control': 'no-cache, no-store, must-revalidate'}
app.app_context().push()

db = SQLAlchemy(app)

if not database_exists(db.engine.url):
    create_database(db.engine.url)

class Users(db.Model):
    username = db.Column("username", db.String(100), primary_key=True)
    password = db.Column("password", db.String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Assignments(db.Model):
    assignment_id = db.Column("assignment_id", db.String(100), primary_key=True, default=uuid.uuid4)
    assignment_name = db.Column("assignment_name", db.String(100), nullable=False)
    assignment_points = db.Column("assignment_points", db.Integer, nullable=False)
    num_of_attempts = db.Column("num_of_attempts", db.Integer, nullable=False)
    deadline = db.Column("deadline", db.DateTime, nullable=False)
    assignment_created = db.Column("assignment_created", db.DateTime, server_default=db.func.now())
    assignment_updated = db.Column("assignment_updated", db.DateTime, onupdate=db.func.now(), server_default=db.func.now())
    username = db.Column("username", db.String(100), db.ForeignKey('users.username'), nullable=False)

    def __init__(self, assignment_id, assignment_name, assignment_points, num_of_attempts, deadline, assignment_created, assignment_updated, username):
        self.assignment_id = assignment_id
        self.assignment_name = assignment_name
        self.assignment_points = assignment_points
        self.num_of_attempts = num_of_attempts
        self.deadline = deadline
        self.assignment_created = assignment_created
        self.assignment_updated = assignment_updated
        self.username = username

db.create_all()
filepath = './users.csv'
with open(filepath, 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            username, password = row
            existing_user = Users.query.filter_by(username=username).first()
            if existing_user is None:
                user = Users(username=username, password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))
                db.session.add(user)
        db.session.commit()

def checkUser(username, password):
    if username is None or password is None:
        return False
    existing_user = Users.query.filter_by(username=username).first()
    if existing_user is None:
        return False
    else:
        if bcrypt.checkpw(password.encode('utf-8'), existing_user.password.encode('utf-8')):
            return True
        else:
            return False

@app.errorhandler(404)
def notFound(error):
    response = app.response_class(status = 404, headers = appHeaders)
    return response

@app.errorhandler(405)
def methodNotAllowed(error):
    response = app.response_class(status = 405, headers = appHeaders)
    return response

@app.after_request
def handle405(response):
    if request.endpoint != 'healthz' and response.status_code == 404 and request.method != 'GET':
        response = app.response_class(status = 405, headers = appHeaders)
    return response  

@app.route('/healthz', methods=['GET'])
def healthz():
    if request.method == 'GET':
        if request.args or request.data:
            response = app.response_class(status=400, headers=appHeadersHealthZ)
            return response
        else:
            try:
                connection = db.engine.connect()
                if connection:
                    response = app.response_class(status=200, headers=appHeadersHealthZ)
                    connection.close()
                    return response
            except:
                response = app.response_class(status=503, headers=appHeadersHealthZ)
                return response
            response = app.response_class(status=200, headers=appHeadersHealthZ)
            return response
        
@app.route('/v1/assignments', methods=['GET', 'POST'])
def assignments():

    if request.method == 'POST':
        if request.args or not request.data:
            response = app.response_class(status=400, headers=appHeaders)
            return response
        elif checkUser(request.authorization.username, request.authorization.password):
            request_data = request.get_json()
            assignmentName = request_data['name']
            assignmentPoints = request_data['points']
            if assignmentPoints < 1 or assignmentPoints > 100:
                return app.response_class(status=400, headers=appHeaders)
            numAttempts = request_data['num_of_attemps']
            deadline = request_data['deadline']
            authUsername = request.authorization.username
            assignment = Assignments(None,assignmentName, assignmentPoints, numAttempts, datetime.strptime(deadline, '%Y-%m-%dT%H:%M:%S.%fZ'), None, None, authUsername)
            db.session.add(assignment)
            db.session.commit()
            responseData = [{
                "id": assignment.assignment_id,
                "name": assignment.assignment_name,
                "points": assignment.assignment_points,
                "num_of_attemps": assignment.num_of_attempts,
                "deadline": assignment.deadline.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                "created": assignment.assignment_created.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                "updated": assignment.assignment_updated.strftime('%Y-%m-%dT%H:%M:%S.%fZ') 
            }]
            response = app.response_class(status=201, headers=appHeaders, response=json.dumps(responseData))
            return response
        else:
            response = app.response_class(status=401, headers=appHeaders)
            return response

    elif request.method == 'GET':
        if request.args or request.data:
            response = app.response_class(status=400, headers=appHeaders)
            return response
        else:
            if checkUser(request.authorization.username, request.authorization.password):
                assignmentResult  = Assignments.query.filter_by(username=request.authorization.username).all()
                assignments = []
                for assignment in assignmentResult:
                    assignments.append({
                        "id": assignment.assignment_id,
                        "name": assignment.assignment_name,
                        "points": assignment.assignment_points,
                        "num_of_attemps": assignment.num_of_attempts,
                        "deadline": assignment.deadline.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        "created": assignment.assignment_created.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        "updated": assignment.assignment_updated.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    })
                response = app.response_class(status=200, headers=appHeaders, response=json.dumps(assignments))
                return response
            else:
                response = app.response_class(status=401, headers=appHeaders)
                return response           


@app.route('/v1/assignments/<assignmentID>', methods=['GET','DELETE', 'PUT'])
def delete_or_put(assignmentID):
    if request.method == 'GET':
        if request.args or request.data:
            response = app.response_class(status=400, headers=appHeaders)
            return response
        else:
            if checkUser(request.authorization.username, request.authorization.password):
                assignment = Assignments.query.filter_by(assignment_id=assignmentID).first()
                if assignment != None:
                    responseData = [{
                        "id": assignment.assignment_id,
                        "name": assignment.assignment_name,
                        "points": assignment.assignment_points,
                        "num_of_attemps": assignment.num_of_attempts,
                        "deadline": assignment.deadline.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        "created": assignment.assignment_created.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        "updated": assignment.assignment_updated.strftime('%Y-%m-%dT%H:%M:%S.%fZ') 
                    }]
                    response = app.response_class(status=200, headers=appHeaders, response=json.dumps(responseData))
                    return response
                else:
                    response = app.response_class(status=403, headers=appHeaders)
                    return response
            else:
                response = app.response_class(status=401, headers=appHeaders)
                return response

    if request.method == 'DELETE':
        if request.args:
            response = app.response_class(status=400, headers=appHeaders)
            return response
        else:
            if checkUser(request.authorization.username, request.authorization.password):
                assignment = Assignments.query.filter_by(assignment_id=assignmentID).first()
                if assignment != None:
                    db.session.delete(assignment)
                    db.session.commit()
                    response = app.response_class(status=204, headers=appHeaders)
                    return response
                else:
                    response = app.response_class(status=404, headers=appHeaders)
                    return response
            else:
                response = app.response_class(status=401, headers=appHeaders)
                return response

# def update_assignment(assignmentID):
    if request.method == 'PUT':
        if request.args or not request.data:
            response = app.response_class(status=400, headers=appHeaders)
            return response
        else:
            if checkUser(request.authorization.username, request.authorization.password):
                assignment = Assignments.query.filter_by(assignment_id=assignmentID).first()
                if assignment != None:
                    request_data = request.get_json()
                    assignment.assignment_name = request_data['name']
                    assignment.assignment_points = request_data['points']
                    if assignment.assignment_points < 1 or assignment.assignment_points > 100:
                        return app.response_class(status=400, headers=appHeaders)
                    assignment.num_of_attempts = request_data['num_of_attemps']
                    assignment.deadline = datetime.strptime(request_data['deadline'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    db.session.commit()   
                    response = app.response_class(status=204, headers=appHeaders)
                    return response
                else:
                    response = app.response_class(status=403, headers=appHeaders)
                    return response
            else:
                response = app.response_class(status=401, headers=appHeaders)
                return response

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)