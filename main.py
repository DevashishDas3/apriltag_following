from threading import Thread, Event
from time import sleep
import cv2
from pid import PID
from video import Video
from bluerov_interface import BlueROV
from pymavlink import mavutil
import numpy as np
import lane_detection as ld
import matplotlib.pyplot as plt












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
pid_forward = PID(K_p=.8, K_i=0.0, K_d=-0.1, integral_limit=1)

# Create the mavlink connection
mav_comn = mavutil.mavlink_connection("udpin:0.0.0.0:14550")
# Create the BlueROV object
bluerov = BlueROV(mav_connection=mav_comn)

frame = None
frame_available = Event()
frame_available.set()


vertical_power = 0  
lateral_power = 0
forward_power = 0

tagD = td.TD()

###NOTE
###I MOVED THIS FUNCTION UP FROM BELOW GET FRAME BECAUSE SEND RC IS USED IN GET FRAME

def _send_rc():
    global vertical_power, lateral_power, forward_power
    bluerov.set_rc_channels_to_neutral()
    bluerov.set_rc_channel(9, 1100)
    mav_comn.wait_heartbeat()
    try:
        while True:
            bluerov.arm()
            mav_comn.wait_heartbeat()
            bluerov.set_vertical_power(int(vertical_power/10))
            bluerov.set_lateral_power(int(lateral_power/10))
            bluerov.set_forward_power(int(forward_power/10))
            sleep(0.2)
    except Exception as e:
        print(e)

###NOTE
###Unknown mode MANUAL
### waits for frame, looks for tag
def get_center(frame):
    return (len(frame),len(frame[0]))

def _get_frame():
    global frame, vertical_power, lateral_power, forward_power

    while not video.frame_available():
        print("Waiting for frame...")
        sleep(0.01)

    frame_count = 0
    try: 
        while True:
            if video.frame_available():
                # k=0
                # if k<1 and frame is not None:
                #     width=int(frame.get(cv2.CAP_PROP_FRAME_WIDTH))
                #     height=int(frame.get(cv2.CAP_PROP_FRAME_HEIGHT))
                #out = cv2.VideoWriter("newoutput.avi", cv2.VideoWriter_fourcc(*'XVID'), 16, (360, 640))
                    # k+=4
                
                lateral_power, vertical_power, forward_power = (0, 0, 0)
                
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

                    ##NOTE This is to show lines
                    lines= ld.my_detect_lines(frame)

                    if lines is None:
                        pass
                    else:
                        #b = ld.detect_lanes(lines, frame)
                        # if b is not None:
                        #     print(f"{len(b)} LANES FOUND")
                        #     plt.imshow(ld.draw_lanes(frame, b))
                        #     plt.show()
                        # else:
                            plt.imshow(ld.draw_lines(frame,lines))
                            plt.show()

                            # print("NO LANES FOUND")
                            # pass


                    ##NOTE this is to print lanes




                    ##NOTE this is to print all the tags stuff
                    if tags == None or len(tags) == 0:

                        b = ld.detect_lanes(lines, frame)

                        if b == None or len(b) == 0:
                            print("no recomended direction")
                            forward_power = 0
                            lateral_power = 0
                        else:
                            #i forgot to make a function that find the closest lane it will just take the first one 
                            lane_center = ld.get_lane_center(b)
                            # direction = ld.recommend_direction(lane_center[0], img)
                            # turning = ld.recommend_turn(lane_center[1])
                           
                            lateral_power = pid_horizontal.update(ld.get_distance_from_lane(lane_center, frame))
                            forward_power = 0.1
                           

                    ##TODO input line detection and make sure the parameters are good
                    ##NOTE from Rome: my line detection is good but my lane detection is bad
                    ##NOTE lanes come out as list of lists not list of lists of list
                    # ## IE: lanes=[[lane],[lane]...] 
                    # ## NOT: lanes=[[[lane]],[[lane]]...]
                    # lines= ld.my_detect_lines(frame)
                    # if lines is None:
                        


                    ##TODO input lane detection and ensure that the lane parameters are good.
                    ##NOTE for Jules: your lane detection should be good but my lines are bad
                    

                    ##TODO Draw component vectors from center to April Tag
        
                    frame = tagD.draw_tag_descriptions(frame)
                    
 

                    # NOTE: Here is where the images are written frame by frame
                    


                    # NOTE: Here is where tags is taken in and then sent to Robot
                    if tags is None or len(tags) == 0:
                        lateral_power, vertical_power, forward_power = tagD.return_PID_values(frame, tags[0], pid_horizontal, pid_vertical, pid_forward)
                        cv2.imwrite(f"frames/framehaha{frame_count:03d}.jpg", frame)
                    



                    
                    # _send_rc()  #Wanted to put in the variables lateral and vertical here, but they are global and SHOULD be accessed
                    print(f"Lateral Power: {lateral_power}\nVertical Power: {vertical_power}\nForward Power: {forward_power}\n it might have moved\n")
                    print(f"Forward Translation: {tags[0].pose_t[2]}\nLateral Translation: {tags[0].pose_t[0]}\nVertical Translation: {tags[0].pose_t[1]}")
                   # print(frame.shape) ## Dr.Saad PUT THIS HERE

                   
                   
                    if b is not None and len(b) > 0:
                        ld.draw_lanes(frame, b)
                        cv2.imwrite(f"frames/framehaha{frame_count:03d}.jpg", frame)
                    


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
        # _get_frame()


except KeyboardInterrupt:
    video_thread.join()
    #rc_thread.join()
    bluerov.disarm()
    print("Exiting...")
