from asyncio.windows_events import NULL
from pyrebase import pyrebase
config = {
    "apiKey": "AIzaSyB30b8Y95IJ2WtYAiYVotGP90sCqsq9F-U",
  "authDomain": "roomv3-c57ad.firebaseapp.com",
  "databaseURL": "https://roomv3-c57ad-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "roomv3-c57ad",
  "storageBucket": "roomv3-c57ad.appspot.com",
  "messagingSenderId": "154542329505",
  "appId": "1:154542329505:web:5ff868a4352b3184302ae0",
  "measurementId": "G-HFCCSRYX21"
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
    db.child("volunteers").child(request.sid).push(request.sid)
    join_room(room)
    
    


@socketio.on('blind: send sdp')
def handle_creating_offer(blind_sdp):
    #blind sdp: string
    print('blind sdp recieved in server')
    # if volunteers_id == None:
    #     return socketio.emit('server: no volunteer found')
    volunteers= db.child("volunteers").get()
    volunteersVal = volunteers.val()
    if volunteersVal ==  None:
        print("server: no volunteer found")
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
       "sdp" : volunteer_invitation['sdp'],
       "id" : request.sid ,
    }
    blindId = volunteer_invitation['blindId']
    db.child("volunteers").child(request.sid).remove()
    volunteers_id.remove(request.sid)
    socketio.emit('server: send volunteer candidate and sdp',volunteer_info, room= blindId )


@socketio.on("Volunteer: accepted call")
def handle_volunteer_accepting_call():
    socketio.emit("server: other volunteer accepted call")

@socketio.on("blind: Call ended")
def handle_blind_call_ending(volunteerID):
    socketio.emit('server: blind Call ended', room = volunteerID)

@socketio.on("volunteer: Call ended")
def handle_volunteer_call_ending(blindID):
    print('volunteer closed')
    blindIdV2 = blindID
    socketio.emit('server: Call ended', room = blindIdV2)



if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0',debug=True, port=5000)





