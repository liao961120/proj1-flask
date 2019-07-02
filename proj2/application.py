import os

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

#channels = dict()
channels = {'testing': {'id': 'testing', 
                        'messages': [
                            {'name': 'Liao', 'time': '07/02/2019, 20:56',  'content': 'hahaha'},
                            {'name': 'Amy', 'time': '07/02/2019, 20:59', 'content': 'hahaha2'}]
                        },
}

@app.route("/")
def index():
    return render_template('index.html')

##### index page: channels #############

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

###### Channel Pages #########
@app.route("/<id>")
def channel(id):
    return render_template('channel.html', channel_id=id)

@socketio.on("load messages")
def load_messages(data):
    channel_id = data["channel-id"]

    if channel_id not in channels.keys():
        channel = {'id': 'null', 'messages': 'null'}
    else:
        channel = channels[channel_id]
    emit(f'load {channel_id} messages', channel, broadcast=True)

@socketio.on("push message")
def save_message(data):
    channel_id = data['channel-id']
    name = data['name']
    content = data['content']
    time = data['time']
    # Save new message
    channels[channel_id]['messages'].append(
        {'name': name , 'time': time, 'content': content}
    )
    # Limit memory: save only 100 most recent messages
    if len(channels[channel_id]['messages']) == 101:
         channels[channel_id]['messages'].pop(0)
    # broadcast message
    emit(f'load {channel_id} messages', channels[channel_id], broadcast=True)
    

if __name__ == '__main__':
    socketio.run(app, debug=True)