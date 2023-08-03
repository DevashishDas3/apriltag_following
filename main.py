from threading import Thread, Event
from time import sleep
import cv2
from pid import PID
from video import Video
from bluerov_interface import BlueROV
from pymavlink import mavutil
import numpy as np
import Lane_detection_files.Romes_Files.lane_detection as ld













# TODO: import your processing functions
import tag_detection as td
from dt_apriltags import Detector

# Create the video object
video = Video()

#video = cv2.VideoCapture("AprilTagTest.mkv")
count = 0
frequency = 100 #dev -> for now


# Create the PID object
pid_vertical = PID(K_p=.12, K_i=0.0, K_d=0.1, integral_limit=1)
pid_horizontal = PID(K_p=.12, K_i=0.0, K_d=-0.1, integral_limit=1) #K_d numbers tried, -.05

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
    global vertical_power, lateral_power
    bluerov.set_rc_channels_to_neutral()
    bluerov.set_rc_channel(9, 1100)
    mav_comn.wait_heartbeat()
    try:
        while True:
            bluerov.arm()
            mav_comn.wait_heartbeat()
            bluerov.set_vertical_power(int(vertical_power))
            bluerov.set_lateral_power(int(lateral_power))
            sleep(0.2)
    except Exception as e:
        print(e)

###NOTE
###Unknown mode MANUAL
### waits for frame, looks for tag
def get_center(frame):
    return (len(frame),len(frame[0]))

def _get_frame():
    global frame, vertical_power, lateral_power

    while not video.frame_available():
        print("Waiting for frame...")
        sleep(0.01)

    frame_count = 0
    try: 
        while True:
            if video.frame_available():
                frame = video.frame()
                print(frame.shape)
                # TODO: Add frame processing here
                
                if frame is not None:
                    
                    
                    frame_count += 1


                    gray = tagD.make_gray(frame)
                    print("finding tag")
                    tags = tagD.detect_tags(gray) # SHOULD return list of tags, MIGHT be None
                    # tags = at_detector.detect(gray, True, ) # SHOULD return list of tags, MIGHT be None 
                    #print(tags)

                    

                    ##TODO input line detection and make sure the parameters are good
                    ##NOTE from Rome: my line detection is good but my lane detection is bad
                    ##NOTE lanes come out as list of lists not list of lists of list
                    ## IE: lanes=[[lane],[lane]...] 
                    ## NOT: lanes=[[[lane]],[[lane]]...]
        


                    ##TODO input lane detection and ensure that the lane parameters are good.
                    ##NOTE for Jules: your lane detection should be good but my lines are bad
                    

                    ##TODO Draw component vectors from center to April Tag
        
                    frame = tagD.draw_tag_descriptions(frame)
                    


                    # NOTE: Here is where the images are written frame by frame
                    


                    # NOTE: Here is where tags is taken in and then sent to Robot
                    if len(tags)>0:
                        lateral_power, vertical_power = tagD.return_PID_values(frame, tags[0], pid_horizontal, pid_vertical)
                        cv2.imwrite(f"frames/frame__{frame_count:03d}.jpg", frame)
                    else:
                        lateral_power, vertical_power=(0,0)



                    
                    # _send_rc()  #Wanted to put in the variables lateral and vertical here, but they are global and SHOULD be accessed
                    print(f"Lateral Power: {lateral_power}\nVertical Power: {vertical_power} \n it might have moved")
                   # print(frame.shape) ## Dr.Saad PUT THIS HERE
                    


    except KeyboardInterrupt:
        return




# Start the video thread
video_thread = Thread(target=_get_frame)
video_thread.start()



# Start the RC thread
# rc_thread = Thread(target=_send_rc)
# rc_thread.start()


# Main loop
try:
    while True:
        mav_comn.wait_heartbeat()
        # _get_frame()


except KeyboardInterrupt:
    video_thread.join()
    rc_thread.join()
    bluerov.disarm()
    print("Exiting...")
