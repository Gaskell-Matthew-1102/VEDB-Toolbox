# This code was written by Matt, used a stackoverflow source and some chatgpt queries asking for Python libraries for frame grabbing and stitching

# Takes in the eye0, eye1, and world timestamps, as well as the two eye vidoes, and downsamples them from 120 fps -> 30 fps
# based on the world timestamps. Ran externally and independent of the viewer application due to its extremely slow pace.

from moviepy.editor import VideoFileClip, ImageSequenceClip
import numpy as np

def closest(world_time, eye0_time, eye1_time):
    print("Loading timestamps...")

    world_time_values = np.load(world_time)
    world_time_list = world_time_values.tolist()
    eye0_time_values = np.load(eye0_time)
    eye0_time_list = eye0_time_values.tolist()
    eye1_time_values = np.load(eye1_time)
    eye1_time_list = eye1_time_values.tolist()

    new_eye0 = []
    new_eye1 = []

    #Technically the correct way to do this, IT IS SO SLOW
    print("Beginning new timestamp list generation...")
    for value in world_time_list:
        # I sourced this code here: https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value
        closest_eye0 = min(eye0_time_list, key = lambda x:abs(x - value))
        new_eye0.append(closest_eye0 - world_time_list[0])
        closest_eye1 = min(eye1_time_list, key=lambda x: abs(x - value))
        new_eye1.append(closest_eye1- world_time_list[0])
    print("Finished new timestamp list generation.")

    # print(len(eye0_time_list)) #80 some thousand
    # print(len(eye1_time_list)) #80 some thousand
    # print(len(world_time_list)) #20 some thousand

    # counter = 0
    # closest_eye0 = min(eye0_time_list, key = lambda x:abs(x - world_time_list[0]))
    # closest_eye1 = min(eye1_time_list, key=lambda x: abs(x - world_time_list[0]))
    # # This is a little bit of a fudged method but SIGNIFICANTLY quicker, and not too far off
    # for i in range(len(eye0_time_list)):
    #     if eye0_time_values[i] < closest_eye0 and eye1_time_values[i] < closest_eye1:
    #         pass
    #     elif counter % 4 == 0:
    #         new_eye0.append(eye0_time_values[i] - world_time_list[0])
    #         new_eye1.append(eye1_time_values[i] - world_time_list[0])
    #     counter = counter + 1
    # print(len(new_eye0)) # 20 some thousand, a little more than world times but not far off, should work
    # print(len(new_eye1)) # same as above

    # for i in range(5):
    #     print(new_eye0[i])
    # for i in range(5):
    #     print(new_eye1[i])
    return new_eye0, new_eye1


# Load the original video
video = VideoFileClip("65967-2021_03_16_17_18_42/421435-eye0.mp4")
new_eye0_list, new_eye1_list = closest("2021_03_16_17_18_42/world_timestamps.npy", "2021_03_16_17_18_42/eye0_timestamps.npy", "2021_03_16_17_18_42/eye1_timestamps.npy")

# Set the target frame rate (30 fps)
target_fps = 30

# Frame rate of the original video (120 fps)
original_fps = video.fps

# Calculate the time interval for keeping frames
interval = original_fps / target_fps  # Every 4th frame (120fps / 30fps)

# List to store frames
frames = []
frames1 = []

# Loop through the video and extract frames at intervals
# for t in range(0, int(video.duration * original_fps), int(interval)):
print("Beginning new eye0 frame capture...")
for t in new_eye0_list:
    if t > 0:
        # frame = video.get_frame(t / original_fps)  # Get the frame at time t
        frame = video.get_frame(t)
        frames.append(frame)
print("Finished new eye0 frame capture.")

print("Beginning new eye1 frame capture...")
for t in new_eye1_list:
    if t > 0:
        # frame = video.get_frame(t / original_fps)  # Get the frame at time t
        frame = video.get_frame(t)
        frames1.append(frame)
print("Finished new eye1 frame capture.")

# Create a new video from the frames
# new_video = video.set_fps(target_fps).subclip(0, video.duration)
# new_video = new_video.fl(lambda gf, t: frames[int(t * target_fps)])

new_video = ImageSequenceClip(frames, fps=30)
new_video1 = ImageSequenceClip(frames1, fps=30)

# Write the result to a new file
print("Writing new eye0 video...")
new_video.write_videofile("eye0_30fps.mp4", fps=target_fps)
print("Finished writing new eye0 video.")
print("Writing new eye1 video...")
new_video1.write_videofile("eye1_30fps.mp4", fps=target_fps)
print("Finished writing new eye1 video.")