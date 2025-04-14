// This code was written by Matt

// var world_video = document.getElementById("worldvideo");
// var eye0_video = document.getElementById("eye0video");
// var eye1_video = document.getElementById("eye1video");

var lastGraphedValue = 1;

var left = 0;
var right = 3;

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

// Function to plot fixations on a separate graph. May refactor later to add them onto an existing graph
// https://plotly.com/javascript/line-charts/
function plotFixations(fixationTimes){
    let timesLength = fixationTimes.length;
    let previousTimeValue = 0;
    let fixationData = [];
    let hidden = true;

    for(let i = 0; i < timesLength; i++){
        let fixationTimeValues = [];
        let nonFixationTimeValues = [];
        fixationTimeValues.push(fixationTimes[i][0], fixationTimes[i][1]);
        nonFixationTimeValues.push(previousTimeValue, fixationTimes[i][0]);
        previousTimeValue = fixationTimes[i][1];

        if(i !== 0){
            hidden = false;
        }

        var nonFixationTrace = {
            x: nonFixationTimeValues,
            y: [0, 0],
            type: 'scatter',
            name: 'Non-Fixation',
            legendgroup: 'Non-Fixation',
            showlegend: hidden,
            marker: {
                color: 'rgb(3, 82, 252)'
            }
        };

        var fixationTrace = {
            x: fixationTimeValues,
            y: [1, 1],
            type: 'scatter',
            name: 'Fixation',
            legendgroup: 'Fixation',
            showlegend: hidden,
            marker: {
                color: 'rgb(252, 7, 3)'
            }
        };

        fixationData.push(nonFixationTrace, fixationTrace);
    }
    // AT SOME POINT HERE QUERY FOR VIDEO TIME AND FIXATION TO THE END IF NOT ALREADY
    var layout = {
        title: {text: 'Eye Fixations'},
        xaxis: {
            title: {text: 'Time'}
        },
        yaxis: {
            title: {text: 'Fixations'}
        },
        width: 500,
        height: 257
    }

    // why was this plotted on gaze lol
    // Plotly.newPlot("gaze", fixationData, layout);
}

//fix this plotly decided to just break lol
function downloadGraphs(linVelFlag, angVelFlag, gazeFlag, fixationFlag){
    const moment = new Date();
    const isoTime = moment.toISOString();

    linear_file_name = 'linear_graph_' + isoTime;
    angular_file_name = 'angular_graph_' + isoTime;
    gaze_file_name = 'gaze_graph_' + isoTime;

    const linearGraphDiv = document.getElementById("linear_velocity");
    const angularGraphDiv = document.getElementById("angular_velocity");
    const gazeGraphDiv = document.getElementById('gaze');

    Plotly.downloadImage(linearGraphDiv, {format:'png', width: 500, height: 257, filename: linear_file_name});
    Plotly.downloadImage(angularGraphDiv, {format:'png', width: 500, height: 257, filename: angular_file_name});
    Plotly.downloadImage(gazeGraphDiv, {format:'png', width: 500, height: 257, filename: angular_file_name})

    // fetch('/download_graphs', {
    //     method: 'POST',
    //     headers: {
    //         'linearGraph': linearGraphDiv,
    //         'angularGraph': angularGraphDiv,
    //         'gazeGraph': gazeGraphDiv,
    //         'linearFileName': linear_file_name,
    //         'angularFileName': angular_file_name,
    //         'gazeFileName': gaze_file_name
    //     },

    // })
}

// I used some of this code: https://jsfiddle.net/adiioo7/zu6pK/light/ to make the video progress bar
jQuery(function ($) {
    $(window).on('load', function() {
        var wvideo = $("#worldvideo")[0];

        var videoMinutes = Math.floor(wvideo.duration/60);
        var videoMinutesString = videoMinutes.toFixed(0);
        videoMinutesString = videoMinutesString.padStart(2, '0');

        var videoSeconds = wvideo.duration%60;
        var videoSecsString = videoSeconds.toFixed(0);
        videoSecsString = videoSecsString.padStart(2, '0');

        var videoTime = videoMinutesString + ":" + videoSecsString;
        $("#totalTime").attr("value", videoTime);

        var defaultTime = '00:00';
        $("#currentTime").attr("value", defaultTime);

        var fixationTimes = [[0.0, 1.0], [2.0, 2.5]];
        plotFixations(fixationTimes);
    });

    $("#dwnld_btn").on('click', function(){
        downloadGraphs();
    })

    $("#worldvideo").on("timeupdate", function(){
        console.log("in here");

        var wvideo = $(this)[0];
        var val = (100/wvideo.duration) * wvideo.currentTime;
        $("#seek-bar").val(val);

        var updatedMinutes = Math.floor(wvideo.currentTime/60);
        var updatedMinsString = updatedMinutes.toFixed(0);
        updatedMinsString = updatedMinsString.padStart(2, '0');

        var updatedSeconds = wvideo.currentTime%60;
        var updatedSecsString = updatedSeconds.toFixed(0);
        updatedSecsString = updatedSecsString.padStart(2, '0');

        var updatedTime = updatedMinsString + ":" + updatedSecsString;
        $("#currentTime").attr("value", updatedTime);

        const linearGraphDiv = document.getElementById("linear_velocity");
        const angularGraphDiv = document.getElementById("angular_velocity");
        const gazeGraphDiv = document.getElementById('gaze');

        left = wvideo.currentTime - 2;
        right = wvideo.currentTime + 2;
        var update = {
            'xaxis.range': [left, right]
        }
        Plotly.update(linearGraphDiv, null, update);
        Plotly.update(angularGraphDiv, null, update);
        Plotly.update(gazeGraphDiv, null, update);
    });

    $("#seek-bar").on("mousedown", function(){
        var wvideo = $("#worldvideo")[0];
        var e0video = $("#eye0video")[0];
        var e1video = $("#eye1video")[0];

        wvideo.pause();
        e0video.pause();
        e1video.pause();
    });

    $("#seek-bar").on("mouseup", function(){
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