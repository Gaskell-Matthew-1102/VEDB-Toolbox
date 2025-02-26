// This code was written by Matt

var world_video = document.getElementById("worldvideo");
var eye0_video = document.getElementById("eye0video");
var eye1_video = document.getElementById("eye1video");

function play(){
    var world_video = document.getElementById("worldvideo")
    var eye0_video = document.getElementById("eye0video")
    var eye1_video = document.getElementById("eye1video")
    if(world_video.paused){
        world_video.play();
        eye0_video.play();
        eye1_video.play();
    }
}

function pause(){
    var world_video = document.getElementById("worldvideo")
    var eye0_video = document.getElementById("eye0video")
    var eye1_video = document.getElementById("eye1video")
    if(!world_video.paused){
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

// Functionality for manipulating videos using Space, Escape, and arrow keys for accessibility and convenience
window.addEventListener('keydown', function(event) {
   var world_video = document.getElementById("worldvideo")
   var eye0_video = document.getElementById("eye0video")
   var eye1_video = document.getElementById("eye1video")

   switch(event.key) {
       case ' ':
           if (world_video.paused) {
               play();
           }
           else if (!world_video.paused) {
               pause();
           }
           break;
       case 'Escape':
           stop_video();
           break;
       case 'ArrowLeft':
           skip_10_backward();
           break;
       case 'ArrowRight':
           skip_10_forward();
           break;
   }
});

// I used some of this code: https://jsfiddle.net/adiioo7/zu6pK/light/ to make the video progress bar
// THIS NEEDS REFACTORING or honestly just changing entirely, right now it shows progress but seeking does not work
jQuery(function ($) {
    $("#worldvideo").on("timeupdate", function(){
        var wvideo = $(this)[0];
        var val = (100/wvideo.duration) * wvideo.currentTime;
        $("#seek-bar").val(val);
    });
    $("#seek-bar").on("mousedown", function(){
        var wvideo = $("#worldvideo")[0];
        var e0video = $("#eye0video")[0];
        var e1video = $("#eye1video")[0];
        wvideo.pause();
        e0video.pause();
        e1video.pause();
    });
    $("seek-bar").on("mouseup", function(){
        var wvideo = $("#worldvideo")[0];
        var e0video = $("#eye0video")[0];
        var e1video = $("#eye1video")[0];

        var seekingTime = $("#seek-bar").val() / (100 / wvideo.duration);
        wvideo.currentTime = seekingTime;
        e0video.currentTime = seekingTime;
        e1video.currentTime = seekingTime;
        wvideo.play();
        e0video.play();
        e1video.play();
    });
});