function getVideos() {
    return [
        document.getElementById("worldvideo"),
        document.getElementById("eye0video"),
        document.getElementById("eye1video")
    ].filter(video => video !== null); // filter in case any aren't found
}

function play() {
    getVideos().forEach(video => {
        if (video.paused) video.play();
    });
}

function pause() {
    getVideos().forEach(video => {
        if (!video.paused) video.pause();
    });
}

function skip(seconds) {
    getVideos().forEach(video => {
        video.currentTime += seconds;
    });
}

function stop() {
    getVideos().forEach(video => {
        video.currentTime = 0;
        video.pause();
    });
}

window.addEventListener('keydown', function(event) {
    switch(event.key) {
        case ' ':
            event.preventDefault(); // prevent page scroll
            const [mainVideo] = getVideos();
            if (mainVideo && mainVideo.paused) {
                play();
            } else {
                pause();
            }
            break;
        case 'Escape':
            stop();
            break;
        case 'ArrowLeft':
            skip(-10);
            break;
        case 'ArrowRight':
            skip(10);
            break;
    }
})
