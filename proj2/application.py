import os

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

channels = dict()

@app.route("/")
def index():
    return render_template('index.html')

@socketio.on("create channel")
def create_channel(data):
    channel_id = data["channel-id"]
    
    # Check Create new empty channel if channel doesn't exist
    if channel_id not in channels.keys():
        channel_dict = {'id': channel_id, 'messages': [],}
        channels[channel_id] = channel_dict

    emit("update", channels, broadcast=True)

@socketio.on('update channel')
def update_channel():
    emit('update', channels, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)