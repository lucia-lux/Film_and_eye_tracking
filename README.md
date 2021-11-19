# Film_and_eye_tracking

This is the script used to collect data from the Tobii T60 eye tracker while participants are watching the trauma film.
For more information on the study paradigm/film, please see:
https://pubmed.ncbi.nlm.nih.gov/31084640/
https://pubmed.ncbi.nlm.nih.gov/26937942/

In the above studies, data were acquired using OpenSesame (Mathôt, S., Schreij, D., & Theeuwes, J. (2012). OpenSesame: An open-source, graphical experiment builder for the social sciences. Behavior Research Methods, 44(2), 314-324. doi:10.3758/s13428-011-0168-7). Due to the specific set up in our lab and the requirements for capturing gaze data during the film, this was not suitable for the intended purpose.
As a result, I put together this script, which basically relies on the following:
- Titta for calibration and capturing data from the Tobii
- Psychopy for stimulus screen/display
- cv2 for video presentatiion
- ffpyplayer for sound

If you need to adjust for different films/input/output directories, just change these in the constants file.

To-do's:
- The audio solution isn't very elegant, as it involves pausing and unpausing the mediaplayer so that the sound syncs properly with the frame presentation. I haven't had time to find a more elegant solution. It would be good to do this though because we've had problems in the past when the presentation computer was running slow, which affected the video frame presentation.
- Calibration: We should test self-paced calibration and/or extending the time each calibration/validation presentation dot is presented for (because the sampling rate of our eye tracker is only 60 Hz, which may make the calibration/validation results more sensitive to outliers due to being based on fewer data points). The former should be relatively easy as there is a dedicated setting in Titta (check the original publication). The latter requires fiddling with the titta code. 
- cv2-related error - line frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) throws an error consistently and needs to be looked at.
- Currently compatible with python 3.6 only due to Tobi/titta requirements.
