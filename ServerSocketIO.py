from pyrebase import pyrebase

config = {
	"apiKey": "AIzaSyCA0PyRw1UdscIk6Od-kkuvZa4WwlhDIAU",
    "authDomain": "room-da00b.firebaseapp.com",
    "databaseURL": "https://room-da00b-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "room-da00b",
    "storageBucket": "room-da00b.appspot.com",
    "messagingSenderId": "732678436627",
    "appId": "1:732678436627:web:0cbd8f297204c473eb0ce6",
    "measurementId": "G-YV0SJVNHHN"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()

from socket import socket

from flask import Flask, render_template, redirect, request, session


from flask.globals import request
from flask_socketio import SocketIO, emit, rooms,send
from flask_socketio import join_room, leave_room

from flask import g

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")


# my_IDlist=None
volunteers_id =[]
volunteers_sdp=dict()
blind =[]
blind_await_ICE=dict()
room ='volunteers'



@app.route('/test')
def register():
    return "working!"


@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    if request.sid in volunteers_id:
        volunteers_id.remove(request.sid)
        db.child("volunteers").child(request.sid).remove()
        leave_room(room)
        
    print('Client disconnected')


@socketio.on('volunteer: connect to room')
def handle_volunteer_connected():
    volunteers_id.append(request.sid)
    db.child("volunteers").child(request.sid).push({'name':'ahmed'})
    join_room(room)
    
    


@socketio.on('blind: send sdp')
def handle_creating_offer(blind_sdp):
    #blind sdp: string
    print('blind sdp recieved in server')
   
    if len(volunteers_id) == 0:
        return socketio.emit('server: no volunteer found')
    
    

    blind_data ={
        "sdp":blind_sdp,
        "id": request.sid,
    }

    blind.append(blind_data)
    print(blind_data)
    socketio.emit('server: send blind connection to all volunteers to create offer',blind_data, room = room)
    


@socketio.on('volunteer: send sdp, candidate and blind id')
def handle_receiving_volunteer_candidate(volunteer_invitation):
    #volunteer_invitation = {
    #   candidate: dict,
    #   sdp : string,
    #   blindId: string
    # }
    print('volunteer sdp & candidate recieved in server')
    print(volunteer_invitation)

    volunteer_info = {
       "candidate" : volunteer_invitation['candidate'],
       "sdp" : volunteer_invitation['sdp']
    }
    blindId = volunteer_invitation['blindId']
    socketio.emit('server: send volunteer candidate and sdp',volunteer_info, room= blindId )
    
   
   





if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0',debug=True, port=5000)





