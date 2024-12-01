function play_pause(){
    var world_video = document.getElementById("worldvideo")
    var eye0_video = document.getElementById("eye0video")
    var eye1_video = document.getElementById("eye1video")
    if(world_video.paused){
        world_video.play();
        eye0_video.play();
        eye1_video.play();
    }
    else{
        world_video.pause();
        eye0_video.pause();
        eye1_video.pause();
    }
}
function skip_10_forward(){
    var world_video = document.getElementById("worldvideo")
    var eye0_video = document.getElementById("eye0video")
    var eye1_video = document.getElementById("eye1video")
    world_video.currentTime += 10;
    eye0_video.currentTime += 10;
    eye1_video.currentTime += 10;
}
function skip_10_backward(){
    var world_video = document.getElementById("worldvideo")
    var eye0_video = document.getElementById("eye0video")
    var eye1_video = document.getElementById("eye1video")
    world_video.currentTime -= 10;
    eye0_video.currentTime -= 10;
    eye1_video.currentTime -= 10;
}
function stop_video(){
    var world_video = document.getElementById("worldvideo")
    var eye0_video = document.getElementById("eye0video")
    var eye1_video = document.getElementById("eye1video")
    world_video.currentTime = 0;
    eye0_video.currentTime = 0;
    eye1_video.currentTime = 0;
    world_video.pause();
    eye0_video.pause();
    eye1_video.pause();
}