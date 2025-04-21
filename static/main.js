$(window).ready(function(){
    $(".loading").fadeOut("slow");
});
// Register the service worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js').then(function(reg) {
        console.log('Service Worker registered with scope:', reg.scope);
    }).catch(function(error) {
        console.log('Service Worker registration failed:', error);
    });
}

// Function to request notification permission and show notification
function showNotification(head, body) {
    // Check notification permission
    if (Notification.permission === 'granted') {
        createNotification(head, body);
    } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(function(permission) {
            if (permission === 'granted') {
                createNotification(head, body);
            } else {
                alert('Notification permission denied.');
            }
        });
    }
}

// Function to create a notification using the Service Worker
function createNotification(head, body, img="/static/2022-04-24-6264bf928d116.png") {
    navigator.serviceWorker.ready.then(function(registration) {
        registration.showNotification(head, {
            body: body,
            icon: img,
            vibrate: [200, 100, 200],
            data: { primaryKey: 1 }
        });
    });
}

setInterval(()=>{
    // let allNote = localStorage.getItem('allWastebinNote');
    // allNote = allNote == null ? [] : JSON.parse(allNote);
    fetch('https://lorawastebin.pythonanywhere.com', {
        method: 'post',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ newBin: 1, seenby: localStorage.getItem('userWastebinToken') }),
    })
    .then(res => res.json())
    .then((datas) => {
        if (datas.length > 0){
            datas.forEach(data => {
                let text = `Wastebin with id: ${data.binId} @(lon: ${data.lon}, lat: ${data.lat}) has reached level: ${((Number(data.level)/183)*100).toFixed(2)}%`;
                // const note = allNote.find((note) => note.id == data.id);
                // if(!note){
                    if (typeof def !== 'undefined' && typeof def.notify === 'function') {
                        // Call the Java function through the JavaScript interface
                        def.notify('New notification for wastebin disposal', text, parseInt(data.id));
                    } else {
                        // Fallback to the browser-specific function
                        showNotification('New notification for wastebin disposal', text);
                    }
                    // allNote.push(data); localStorage.setItem('allWastebinNote', JSON.stringify(allNote));
                // }

                fetch('https://lorawastebin.pythonanywhere.com', {
                    method: 'post',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ newNotify: 1, binId: data.binId, userToken: localStorage.getItem('userWastebinToken'), binDate: data.date }),
                })
                .then(res => res.json())
                .then(data => console.log(data))
                .catch(err => console.error(err));
            });
        }
    })
    .catch(err => console.error(err));
}, 5000)

window.onload = function () {
    let userToken = localStorage.getItem('userWastebinToken');
    fetch('https://lorawastebin.pythonanywhere.com/get-token')
    .then(response => response.json())
    .then(data => {
        if(data.user_token){
            !userToken && localStorage.setItem('userWastebinToken', data.user_token);
            // console.log(data.user_token, userToken);
        }
    });
    if (Notification.permission === 'granted') {

    } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(function(permission) {
            if (permission === 'granted') {

            } else {
                alert('Notification permission denied.');
            }
        });
    } // Start loading the page only after the location is retrieved
};