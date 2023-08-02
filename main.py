from threading import Thread, Event
from time import sleep
import cv2
from pid import PID
from video import Video
from bluerov_interface import BlueROV
from pymavlink import mavutil
import numpy as np


# TODO: import your processing functions
import tag_detection as td
from dt_apriltags import Detector

# Create the video object
video = Video()

#video = cv2.VideoCapture("AprilTagTest.mkv")



# Create the PID object
pid_vertical = PID(K_p=0.1, K_i=0.0, K_d=0.01, integral_limit=1)
pid_horizontal = PID(K_p=0.1, K_i=0.0, K_d=0.01, integral_limit=1)
# Create the mavlink connection
mav_comn = mavutil.mavlink_connection("udpin:0.0.0.0:14550")
# Create the BlueROV object
bluerov = BlueROV(mav_connection=mav_comn)

frame = None
frame_available = Event()
frame_available.set()


vertical_power = 0  
lateral_power = 0  

tagD = td.TD()

###NOTE
###I MOVED THIS FUNCTION UP FROM BELOW GET FRAME BECAUSE SEND RC IS USED IN GET FRAME

def _send_rc():
    bluerov.set_vertical_power(vertical_power)
    bluerov.set_lateral_power(lateral_power)



def _get_frame():
    global frame

    while not video.frame_available():
        print("Waiting for frame...")
        sleep(0.01)

    try:
        
        while True:
            if video.frame_available():
                
                frame = video.frame()
                # TODO: Add frame processing here
                
                if frame is not None:
                    gray = tagD.make_gray(frame)
                    print("finding tag")
                    tags = tagD.detect_tags(gray) # SHOULD return list of tags, MIGHT be None
                    # tags = at_detector.detect(gray, True, ) # SHOULD return list of tags, MIGHT be None

                  
                    #print(tags)
                    
                    # TODO: set vertical_power and lateral_power here
                    if len(tags)>0:
                        lateral_power, vertical_power = tagD.return_PID_values(frame, tags[0], pid_horizontal, pid_vertical)
                    else:
                        lateral_power, vertical_power=(0,0)
                    #_send_rc()  #Wanted to put in the variables lateral and vertical here, but they are global and SHOULD be accessed


                    print(f"Lateral Power: {lateral_power}\nVertical Power: {vertical_power} \n it might have moved")
                    print(frame.shape) ## Dr.Saad PUT THIS HERE
                    


    except KeyboardInterrupt:
        return




# Start the video thread
video_thread = Thread(target=_get_frame)
video_thread.start()



# Start the RC thread
rc_thread = Thread(target=_send_rc)
rc_thread.start()


# Main loop
try:
    while True:
        mav_comn.wait_heartbeat()
        _get_frame()


except KeyboardInterrupt:
    video_thread.join()
    rc_thread.join()
    bluerov.disarm()
    print("Exiting...")
