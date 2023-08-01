from threading import Thread, Event
from time import sleep
import cv2
from pid import PID
from video import Video
from bluerov_interface import BlueROV
from pymavlink import mavutil


# TODO: import your processing functions
import tag_detection as td

# Create the video object
video = Video()
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


y_pid = PID(0.2, 0.0, 0.0, 100)
x_pid = PID(0.2, 0.0, 0.0, 100)


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
                

                # TODO: set vertical_power and lateral_power here
                
                
                _send_rc()
                print(frame.shape)

    except KeyboardInterrupt:
        return


def _send_rc():
    bluerov.set_vertical_power(vertical_power)
    bluerov.set_lateral_power(lateral_power)


# Start the video thread
video_thread = Thread(target=_get_frame)
video_thread.start()

# Start the RC thread
rc_thread = Thread(target=_send_rc)
rc_thread.start()


# Main loop
try:
    i = 0
    while True:
        mav_comn.wait_heartbeat()
        _get_frame()
        gray = td.make_gray(frame)
        tag = td.detect_tags(gray)[i]
        td.send_PID_control(gray, tag, *td.get_distance_from_center(frame, tag.center))
        


except KeyboardInterrupt:
    video_thread.join()
    rc_thread.join()
    bluerov.disarm()
    print("Exiting...")
