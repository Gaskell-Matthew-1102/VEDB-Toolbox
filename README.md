# The VEDB Toolbox
The Visual Experience Database (VEDB) consists of over 700 sessions of videos/data collected from subjects wearing specialized headsets while doing everyday tasks. To address the data's unique format, the VEDB Toolbox is a user-oriented web application designed to analyze data and generate interactive graphs from them alongside the videos. An algorithm analyzes the video/data to determine whether subjects are focusing on specific points. This application is primarily used within UNR, with the potential for wider adoption for vision science research and product development.
## Accessing the Toolbox
In order to acquire the files to run the application locally, either download the zip or clone into the repository. The zip can be found in a dropdown after clicking the green code button at the top of the webpage. If you are familiar with Git, clone into the repository by running the following command in a terminal at a convenient location of your choosing:
```
git clone https://github.com/Gaskell-Matthew-1102/VEDB-Toolbox.git
```
Alternatively, an option is present to clone into the repository with GitHub Desktop, which will take you to that application and prompt you on completing the clone. If you downloaded the zip file, extract the files in a convenient location.
## Installing Requirements
The Toolbox uses many Python libraries. To install these, open a terminal and navigate to the main directory of the files you previously downloaded. In this, there is a file named 'requirements.txt'. Python and Pip are necessary to install these. Python can be installed from their website. Pip can also be installed through this, or through the command line. To ensure pip is installed, please use the following command:
```
pip --version
```
Once pip has been installed and verified, run the following:
```
pip install -r requirements.txt
```
Now the Toolbox is ready to be run.
## Running the Toolbox
In the same general directory, a file named 'run_me.py' can be found. This can be ran from the command line:
```
python run_me.py
```
The Toolbox is now locally accessible at http://127.0.0.1:5000. Navigating to this link in your browser (Chrome recommended) will bring you to the login page of the Toolbox.
## Using the Toolbox
A tutorial is provided on the site and can be accessed through a drop-down at the top of the landing page. For convenience, it is transcribed here as well.
#### Step 1: Register and Login
An account is required to access the Toolbox. On our landing page, you can register an account with an email address, username, and password. A captcha is provided for security reasons, and your information will be securely stored. Once you have registered an account, you will be automatically logged in, or if you have already registered an account, you can just log in with those credentials.
#### Step 2: Acquire Files
Currently, the files for the VEDB are located in multiple places. The video files need authorization to acquire, however the data files are hosted by the Open Science Foundation (OSF). Either download and unzip the data files from this link, or copy the download link, and save it for later. All of the video files are required, however, the only two data files that are currently conventionally required are 'odometry.py' and 'gaze.npz'. However, some datasets don't have the gaze file, and if not provided the visualizer will still function, it will just be missing gaze position graphs and fixation detection.
#### Step 3: Upload Files
The file upload screen is presented after logging in. Here, files for both the data and the videos of the VEDB can be uploaded. For the video files, the three videos (two eyes, one world) are required. The CSV file is optional. For the data files, only odometry.pldata is required. For the visualizer and the fixation detection algorithm to work, both odometry.pldata and gaze.npz are required. However, you may upload as many of the other data files are you'd like, for conventionality. Files can be drag and dropped from File Explorer or Finder, and for the data files found on OSF, a link to that download may be entered, and the system will download and unzip the files for you.
#### Step 4: Enter Visualizer
Once both sets of files have been correctly uploaded, a button will appear to allow you to enter the visualizer. This may take a little bit of time, as it needs to generate the graphs and begin running fixation detection. After these are completed, the visualizer will appear, with the three videos, video controls and progress bar, the three graphs, and navigation controls to return to file upload, to log out, or to download images of the generated graphs. Once playing, the graphs will move in time with the videos, showing recorded data as it was seen by the participant. The videos can be paused, stopped and reset, or skipped through, either with the skip ten seconds buttons or by dragging the progress bar.
#### Step 5: Resetting or Exiting
To change the files to be visualized, you may exit the viewer by clicking the exit button at the top. This will bring you back to the file upload screen, where you can select the option to upload different video and/or data files. The new files will go through the same review process as before, and n you can re-enter the visualizer. If you would like to exit the program all together, you can either exit the visualizer first and then close the window, or log-out and then close the window. Your login will be cached if you return shortly, but you will have to re-login if coming back after a while.
## Acknowledgements
This project was developed in Fall of 2024 and Spring of 2025 as part of the capstone courses CS 425 Software Engineering and CS 426 Senior Projects in Computer Science at the University of Nevada, Reno. Development was advised by Paul MacNeilage and Mark Lescroart within the Psychology department at UNR.