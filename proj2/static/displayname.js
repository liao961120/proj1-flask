document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('div.displayName').style.display = 'none';
    document.querySelector('button#updateDisplayName').style.display = 'none';

    // Prompt user to enter display name
    if (!localStorage.getItem('DisplayName')) {
        alert('Enter a display name.');
        document.querySelector('div.displayName').style.display = 'block';
    } else {
        out_str = `Display Name: ${localStorage.getItem('DisplayName')}`
        document.querySelector('#displayName').innerHTML = out_str;
    };
    
    // Set display name for the first time
    document.querySelector('button#newDisplayName').onclick = () => {
        let name = document.querySelector('input#display').value
        if (name.trim() === '') {
            alert('Empty display name not allowed!');
            return 0
        };

        // Update display name
        localStorage.setItem('DisplayName', name.trim());
        out_str = `Display Name: ${name.trim()}`
        document.querySelector('#displayName').innerHTML = out_str;

        // Hide input field
        document.querySelector('div.displayName').style.display = 'none';
        // Show update button
        document.querySelector('button#updateDisplayName').style.display = 'block';
    };

    // Update display name
    document.querySelector('button#updateDisplayName').onclick = () => {
        document.querySelector('div.displayName').style.display = 'block';
        document.querySelector('button#updateDisplayName').style.display = 'none';
    }
});