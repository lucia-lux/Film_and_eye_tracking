
import PySimpleGUI as sg
import os
from ffpyplayer.player import MediaPlayer
import time
import pygaze
import cv2
import numpy as np
import math
from psychopy.visual import ImageStim
from pygaze.display import Display
from pygaze.screen import Screen
import datetime
import pygaze.libtime as timer
from pygaze.keyboard import Keyboard
#from pygaze.eyetracker import EyeTracker
#from pygaze.logfile import Logfile
import pickle
import pandas as pd
from psychopy import visual, monitors
from psychopy import core, event
from titta import Titta, helpers_tobii as helpers
from constants import *
# GUI
layout = [[sg.Text("Please enter participant ID")],[sg.Input("")], [sg.Text("Pilot or testing (1 = pilot, 0 = testing)")],[sg.Input("")],[sg.Button("Continue")],[sg.Button('Submit', visible=False, bind_return_key=True)]]

# Create the window
window = sg.Window("Start film", layout)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event in ("Continue","Submit",sg.WIN_CLOSED):
#    if event == "Continue" or event == "Submit" or event == sg.WIN_CLOSED:
        break

window.close()
participant_id = int(list(values.values())[0])
pilot = int(list(values.values())[1])
print("pnum: ", participant_id)
print("pilot: ",pilot)

# Calibrate the eye tracker.
# Monitor/geometry - need to adapt for Tobii screen
MY_MONITOR                  = 'trackMonitor' # needs to exists in PsychoPy monitor center
FULLSCREEN                  = True
SCREEN_RES                  = [1280, 1024]
SCREEN_WIDTH                = 33.8 # cm
VIEWING_DIST                = 57 #  # distance from eye to center of screen (cm)

mon = monitors.Monitor(MY_MONITOR)  # Defined in defaults file
mon.setWidth(SCREEN_WIDTH)          # Width of screen (cm)
mon.setDistance(VIEWING_DIST)       # Distance eye / monitor (cm)
mon.setSizePix(SCREEN_RES)

# Window set-up (this color will be used for calibration)
win = visual.Window(monitor = mon, fullscr = FULLSCREEN, color=(-1, -1, -1),
                    screen=1, size=SCREEN_RES, units = 'deg')

# ET settings
# need this to call the correct settings
et_name = 'Tobii T60'
# use dummy for testing (when no eye tracker connected)
dummy_mode = False
bimonocular_calibration = False

# Change any of the default settings?
settings = Titta.get_defaults(et_name)
settings.FILENAME = os.path.join(dirpath,'titta_'+str(participant_id)+'.tsv')
print(settings.FILENAME)

# Connect to eye tracker and calibrate
tracker = Titta.Connect(settings)
if dummy_mode:
    tracker.set_dummy_mode()
tracker.init()

# Calibrate
if bimonocular_calibration:
    tracker.calibrate(win, eye='left', calibration_number = 'first')
    tracker.calibrate(win, eye='right', calibration_number = 'second')
else:
    tracker.calibrate(win)
tracker.send_message('_'.join(['START_CALIBRATION', str(participant_id)]))
all_calibs = tracker.calibration_history()
print("calib_hist:", all_calibs)
df = pd.DataFrame(all_calibs)


# Save calibration data
df.to_csv(settings.FILENAME + '_calib.tsv', sep='\t')
#tracker.save_calibration(os.path.join(dirpath,"calib_"+str(participant_id)))

DISPTYPE = 'psychopy'
dispsize = (400, 300)
disp = Display(disptype = DISPTYPE, screennr = 1)
scr1 = Screen()
scr1.set_background_colour(colour = (0,0,0))

#defaults.LOGFILE = ('C:\\Users\\testing\\Desktop\\luzia_testing\\film\\data')
#defaults.LOGFILENAME = os.path.join(defaults.LOGFILE, str(participant_id)+'_data.tsv')
kb = Keyboard()
#TRACKERTYPE = 'tobii'
#TRACKERSERIALNUMBER = "TT060-301-14200900"
#tracker = EyeTracker(disp,TRACKERTYPE)


#settings.LOGFILE = (defaults.LOGFILENAME)

# Create a Logfile instance that keeps track of when videos start.
#log = Logfile(filename = LOGFILE)
# Write a header to the log file.
#log.write(['date', 'time', 'timestamp'])

# Screen for instructions
textscr = Screen()
textscr.set_background_colour(colour = (0,0,0))
textscr.draw_text("Press any key to start the video.",fontsize=24)
#textscr.set_background_colour = (0,0,0)

# some info about the video
#filename = "C:\\Users\\luzia.troebinger\\CortEx\\experiment_folder_python\\try_audio_ffpyplayer\\video_out.mp4"
# paths to videos for pilot and testing:
if pilot:
    filmname = film_pilot
else:
    filmname = film_test

video=cv2.VideoCapture(filmname)
# video height and width
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
#width = 1920
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
#height = 1080
nframes = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
framerate = float(video.get(cv2.CAP_PROP_FPS))
# compute the frame duration (in ms)
framedur = 1000.0 / framerate

# Reset the current stimscr.
scr1.clear()

# player for film - pause for now
player = MediaPlayer(filmname, ff_opts ={'paused': True, 'autoexit': True, 'sync': 'video', 'vn': False})

# For PsychoPy, prepare a new ImageStim.
if DISPTYPE == 'psychopy':
    # Create a black frame, formatted as an all-zeros NumPy array.
    frame = np.zeros((height, width, 3), dtype=float)
    # Now create a PsychoPy ImageStim instance to draw the frame with.
    stim = ImageStim(pygaze.expdisplay, image=frame, size=(width, height))
    # When DISPTYPE='psychopy', a Screen instance's screen property is a list
    # of PsychoPy stimuli. We would like to add the ImageStim we just created
    # to that list, and record at what index in the list it was added.
    # First we get the current length of the stimscr's list of stimuli, which
    # will be the index at which the new ImageStim will be assigned to.
    stim_index = len(scr1.screen)
    # Then we add the ImageStim to the stimscr. Every time you call
    # disp.fill(stimscr) and then disp.show(), all stimuli in stimscr
    # (including the ImageStim) will be drawn.
    scr1.screen.append(stim)

# Wait until the participant presses any key to start.
disp.fill(textscr)
disp.show()
kb.get_key(keylist=None, timeout=None, flush=True)

tracker.start_recording(gaze_data = True, store_data = True)
# now unpause player
player.toggle_pause()
# log start of film.
# Log trial specifics to gaze data file.
#timer.pause(5)
tracker.send_message("VIDNAME %s; EXPTIME %d; PCTIME %s" % \
    (filmname, timer.get_time(), \
    datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')))

for framenr in range(nframes):
    loadstart = timer.get_time()
    # read the video frame, grabbed indicates success
    grabbed, frame=video.read()
    # get the corresponding audio
    audio_frame, val = player.get_frame()
#    while audio_frame is None or audio_frame == 0:
#        audio_frame, val = player.get_frame()

#    print("audio_frame:", audio_frame)
    if frame is None:
        grabbed = 0
    if grabbed:# and framenr > 0:
        # for psychopy display:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert the frame form unsigned integers between 0 and 255
        # to floats between 0 and 1.
        frame = frame / 255.0
        # Flip the frame upside-up.
        frame = np.flipud(frame)

    if not grabbed:
        frame = np.zeros((height, width, 3), dtype=float)

    scr1.screen[stim_index].setImage(frame)
    disp.fill(scr1)
    frametime = disp.show()

    if val != 'eof' and audio_frame is not None:

        img, t = audio_frame



    loaddur = frametime - loadstart
    #pause timer to get full frame duration
    timer.pause(int(framedur - (loaddur)))

    pc_frametime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')
    tracker.send_message("FRAMENR %d; TIME %.3f; PCTIME %s" % \
        (framenr, frametime, pc_frametime))


# Log the end of the trial.
tracker.send_message("TRIALSTOP")

# Clear the display (showing the background colour).
disp.fill()
disp.show()
video.release()
disp.close()
# Stop recording eye movements.
tracker.stop_recording(gaze_data = True)
tracker.save_data()

f = open(settings.FILENAME[:-4] + '.pkl', 'rb')
gaze_data = pickle.load(f)
msg_data = pickle.load(f)

# Save data and messages
df = pd.DataFrame(gaze_data, columns=tracker.header)
df.to_csv(settings.FILENAME[:-4] + '.tsv', sep='\t')
df_msg = pd.DataFrame(msg_data,  columns = ['system_time_stamp', 'msg'])
df_msg.to_csv(settings.FILENAME[:-4] + '_msg.tsv', sep='\t')

#old_file = os.path.join("C:\\Users\\testing\\Desktop\\luzia_testing\\film\\data", "999_TOBII_output.tsv")
#new_file = os.path.join("C:\\Users\\testing\\Desktop\\luzia_testing\\film\\data", str(participant_id)+"TOBII_output.tsv")
#os.rename(old_file, new_file)
