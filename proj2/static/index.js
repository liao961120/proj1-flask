document.addEventListener('DOMContentLoaded', () => {
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {
        // Request data on connect
        socket.emit('update channel');

        // Create new channel
        document.querySelector('button#createChannel-submit').onclick = () => {
            const id = document.querySelector('input#createChannel').value.trim().replace(/\s+/g, '-')

            // Check empty channel name
            if (!id) {alert('Empty Channel name not allowed'); return;}

            // Check conflicting channel names
            const curr_channels = document.querySelectorAll('.channel')
            let currChannelIds = getCurrChannelIDs();
            if (currChannelIds.includes(id)) {alert('Channel name already used!'); return;}

            // Send new channel id to server
            socket.emit('create channel', {'channel-id': id});
        };

    });//end socker connect

    // Create and/or update channel and messages
    socket.on('update', data => updateChannel(data));

});// end DOMContentLoaded

// helpers
function updateChannel(json) {
    let ids = Object.keys(json);
    let currChannelIds = getCurrChannelIDs();
    ids.forEach(channel_id => {
        // Update existing channel
        if (currChannelIds.includes(channel_id)) {
            loadChannel(json[channel_id]);
        // Create New channel if ID not found
        } else {
            createChannel(channel_id);
            loadChannel(json[channel_id]);
        };
    });
};

function createChannel(id) {
    const div = document.createElement('div');
    div.className = 'channel';
    div.id = id;
    // Add New channel
    document.querySelector('.channels').append(div);
};

function loadChannel(json) {
    // Title
    const title = `<h2>Channel: <a href='./${json.id}'>${json.id.replace(/\-/g, ' ')}</a></h2>`;

    // Update div#channel-id
    document.querySelector(`#${json.id}`).innerHTML = title;
};

function getCurrChannelIDs() {
    const curr_channels = document.querySelectorAll('.channel');
        let curr_channel_ids = [];
        for (i = 0; i < curr_channels.length; ++i) {
            curr_channel_ids.push(curr_channels[i].id);
        };
    return curr_channel_ids;
};