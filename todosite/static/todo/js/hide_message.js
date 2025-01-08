// static/js/hide_message.js

window.onload = function() {
    setTimeout(function() {
        var message = document.getElementById('message');
        if (message) {
            message.style.display = 'none';
        }
    }, 5000);  
};
