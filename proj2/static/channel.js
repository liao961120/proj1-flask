document.addEventListener('DOMContentLoaded', () => {
    const channel_id = document.URL.split('/').reverse()[0];  // basename
    var datetimeOpt = {year: 'numeric', month:'2-digit', day:'2-digit', hour: 'numeric', minute: '2-digit', hour12: false, timeZone: 'Asia/Taipei'};
    
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // Require channel messages
    socket.on('connect', () => {
        socket.emit('load messages', {'channel-id': channel_id});

        // Send Message
        document.querySelector('#send').onclick = () => {
            content = document.querySelector('#myMessage').value.trim().replace(/\n/g, "<br>");
            displayName = getDisplayName();
            var today = new Date();
            const timestamp = today.toLocaleDateString('en-US', datetimeOpt)
            socket.emit(`push message`,
                {'channel-id':channel_id, 'time': timestamp,
                'name': displayName, 'content': content});
            
            // Clean up textarea
            document.querySelector('textarea#myMessage').value = '';
        };
    });

    // Load channel messages
    socket.on(`load ${channel_id} messages`, channel => loadMessages(channel));

});

///// Helpers //////

function loadMessages(channel) {
    // Checking
    if (channel['id'] === 'null') return;
    if (channel['messages'].length === 0) return;

    const message_lst = document.createElement('ul');
    message_lst.id = 'history';
    for (i=0; i < channel.messages.length; ++i) {
        let message = document.createElement('li');
        message.innerHTML = `
            <span style='font-size:0.95em;'>${channel.messages[i]['name']} </span> 
            <span style='font-size:0.85em;color:grey;'> ${channel.messages[i]['time']}:</span><br>
            ${channel.messages[i]['content']}`;
        message_lst.append(message);
    };
    
    // Update div#channel-id
    document.querySelector('#messages').innerHTML = '';
    document.querySelector('#messages').append(message_lst);

    // Scroll to bottom in message-box
    let objDiv = document.querySelector(".message-box");
    objDiv.scrollTop = objDiv.scrollHeight;
};


function getDisplayName() {
    var displayName = localStorage.getItem('DisplayName');
    if (!displayName) {
        alert('You did not enter a display name before!')
        return;
    };
    return displayName;
};