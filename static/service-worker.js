// service-worker.js

self.addEventListener('push', function(event) {
    const options = {
        body: event.data ? event.data.text() : 'New notification from Adekola',
        icon: 'https://salimdotpy.pythonanywhere.com/static/2022-04-24-6264bf928d116.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: '1'
        },
        actions: [
            {
                action: 'explore',
                title: 'View Details', // Customize this button text
                // icon: '/static/images/explore-icon.png' // Optional icon for button
            },
            {
                action: 'close',
                title: 'Dismiss',  // Customize this button text
                // icon: '/static/images/close-icon.png' // Optional icon for button
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('New message', options)
    );
});
