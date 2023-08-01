from dt_apriltags import Detector
import cv2
import matplotlib.pyplot as plt
import numpy as np
from pid import *
import numpy as np
from math import isclose
#if u need it
# def draw_line_to_april_tag(camera_center, april_tag_center):
#     # Unpack the coordinates of the camera and AprilTag centers
#     cam_x, cam_y = camera_center
#     tag_x, tag_y = april_tag_center

#     # Create a plot
#     plt.figure()

#     # Draw the camera center point
#     plt.scatter(cam_x, cam_y, color='red', label='Camera Center')

#     # Draw the AprilTag center point
#     plt.scatter(tag_x, tag_y, color='blue', label='AprilTag Center')

#     # Draw the line connecting the camera center to the AprilTag center
#     plt.plot([cam_x, tag_x], [cam_y, tag_y], 'g--', label='Line to AprilTag')

#     # Set the axis limits to ensure both points are visible
#     plt.xlim(min(cam_x, tag_x) - 1, max(cam_x, tag_x) + 1)
#     plt.ylim(min(cam_y, tag_y) - 1, max(cam_y, tag_y) + 1)

#     # Add labels and legend
#     plt.xlabel('X')
#     plt.ylabel('Y')
#     plt.title('Line from Camera Center to AprilTag Center')
#     plt.legend()

#     # Show the plot
#     plt.show()


def get_video(src="AprilTagTest.mkv"):
    vcap=cv2.VideoCapture(src)
    return(vcap)

### NEEDS TESTING TO SEE IF vcap.read()[1] WORKS
def get_frame(vcap):
    frame = vcap.read()[1] #Should return that frame is vcap.read()[1] on the basis that ret,frame = vcap.read() works
    return(frame)

def make_gray(frame):
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) # convert to grayscale
    return gray

def detect_tags(gray):

    at_detector = Detector(families='tag36h11',
                        nthreads=1,
                        quad_decimate=1.0,
                        quad_sigma=0.0,
                        refine_edges=1,
                        decode_sharpening=0.25,
                        debug=0)
    

    cameraMatrix = np.array([ 1060.71, 0, 960, 0, 1060.71, 540, 0, 0, 1]).reshape((3,3))
    camera_params = ( cameraMatrix[0,0], cameraMatrix[1,1], cameraMatrix[0,2], cameraMatrix[1,2] )
    tags = at_detector.detect(gray, True, camera_params, tag_size  = 0.1)

    
    return tags

def get_center(img):
    # gets the center of image as a tuple 
    #or literally "return img.center" lol one line
    vertical = len(img)
    horizontal = len(img[0]) 
    return horizontal/2, vertical/2

def get_distance(point1, point2):
    # returns distance of two points x, y
    
    return (point1[0] - point2[0]), (point1[1] - point2[1])

def get_distance_from_center(img, point):
    return get_distance(point, get_center(img))

def get_percentage(img, H_d, V_d):
    
    return H_d/len(img[0]), V_d/len(img)
    
def draw_line(img, lines, color=(255,0,0), thickness=10):
    # draws line on image
    if lines is None:
            pass
    else:
        for line in lines:
            if line is None or len(line) == 0:
                pass
            else:
                x1, y1, x2, y2 = line[0]
                cv2.line(img, (x1, y1), (x2, y2), color, thickness)
        
    return(img)

def half_image(img):
    # returns half image
    halfimg = img[img.shape[0]/2:img.shape[1]]
    return halfimg

def draw_line_center(img, tag, color=(255,0,0),thickness=10):
    #draws line from center to tag
    center=get_center(img)
    cv2.draw_line(img,center, tuple(map(int(tag.center))),color,thickness)
    
    #cv2.line(img, tuple(map(int, tag.center)), tuple(map(int, np.array(img.shape[1::-1])/2)), (255, 0, 0), 3)

def send_PID_control(img, tag, x_pid, y_pid):
    # takes in img, tag (the first tag), two PIDs to send final control signals
    horizontal_error = tag.center[0] - (img.shape[1]/2)
    vertical_error = tag.center[1] - (img.shape[0]/2)
    
    x_output = x_pid.update(horizontal_error)
    y_output = y_pid.update(vertical_error)

    return x_output, y_output

    
def main():
    vcap=get_video("AprilTagTest.mkv")
    ret, frame = vcap.read()
    ##Need to fix the while ret to make
    while ret:
        try:
            ##TODO GET IMAGE FROM VIDEO USING GET FRAME
            frame = get_frame(vcap)
            
            ##TODO MAKE THAT FRAME GRAYSCALE
            gray = make_gray(frame)

            ##TODO DETECT TAGS IN THAT GRAY IMAGE USING GRAYSCALE OUTPUT
            tags = detect_tags(gray)

            ##TODO GET DISTANCE FROM CENTER OF APRIL TAG TO CENTER OF CAMERA USING CAMERA RESOLUTION AND APRILTAG LOCATION
            Total_Distance = np.hypot(get_distance_from_center(gray, tags[0]))

            ##TODO DRAW LINE TO CENTER OF APRIL TAG
            draw_line_center(frame, tags[0])

            ##TODO PUT X_DISTANCE AND Y_DISTANCE INTO PID AND TAKE OUTPUT
            x_distance, y_distance = get_distance_from_center(frame, tags[0].center)
    
            ##TODO GET THAT OUTPUT AND SEND IT INTO TO MAV CONTROLS
            send_PID_control(frame, tags[0], x_distance, y_distance)

            ret, frame= vcap.read()
            

        ##TODO MAKE THIS A LOOP USING TRY AND EXCEPT FOR KEYBOARD INTERRUPT

        except KeyboardInterrupt:
            print("Closed reader")





    
    