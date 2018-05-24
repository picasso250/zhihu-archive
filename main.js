// only support IE9+
ready(function() {
    document.getElementById('f').addEventListener('submit', function (e) {
        e.preventDefault();

        var url = document.getElementById('url').value;
        var msg = document.getElementById('p');

        msg.textContent = "loading...";

        var request = new XMLHttpRequest();
        request.open('GET', '/index.php?url=' + encodeURIComponent(url), true);

        request.onload = function () {
            if (request.status >= 200 && request.status < 400) {
                // Success!
                var data = (request.responseText);
                msg.textContent = data;
            } else {
                // We reached our target server, but it returned an error

            }
        };

        request.onerror = function () {
            // There was a connection error of some sort
        };

        request.send();
    });
});

function ready(fn) {
    if (document.readyState != 'loading') {
        fn();
    } else if (document.addEventListener) {
        document.addEventListener('DOMContentLoaded', fn);
    } else {
        document.attachEvent('onreadystatechange', function () {
            if (document.readyState != 'loading')
                fn();
        });
    }
}