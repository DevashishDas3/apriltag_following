from dt_apriltags import Detector
import cv2
import matplotlib.pyplot as plt
import numpy as np
from pid import *
import numpy as np
from math import isclose

def apriltag_detect(img, x_pid, y_pid):
        if img is None:
            pass
        else:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
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
            color_img = img
        #depth
            for tag in tags:
                print(tag.center)
                cv2.line(color_img, tuple(map(int, tag.center)), tuple(map(int, np.array(img.shape[1::-1])/2)), (255, 0, 0), 3) 

                #displaced_x = tag.pose_t[0][0]
                displaced_x = tag.center[0] - (img.shape[1]/2)
                #print(displaced_x)
                #displaced_depth = tag.pose_t[1][0]
                displaced_y = tag.center[1] - (img.shape[0]/2)
                #print(displaced_y)

                x_output = 0
                y_output = 0

                #while(not isclose(x_output, tag.center[0]) and not isclose(y_output, tag.center[1])):
             
                x_output = x_pid.update(displaced_x)
            
                y_output = y_pid.update(displaced_y)
                return((x_output, y_output))

            # brov.set_vertical_power(y_output)
            # brov.set_lateral_power(x_output)

        
        #print((x_output, y_output))

        
        plt.imshow(color_img)
        plt.show()