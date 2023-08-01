from dt_apriltags import Detector
import cv2
import matplotlib.pyplot as plt
import numpy as np
from pid import *
import numpy as np
from math import isclose

from bluerov_interface import BlueROV as brov

def april_test(video, x_output, y_output):
    vcap = cv2.VideoCapture(video)

    width = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # output_file = 'april_tags.avi'
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # output_video = cv2.VideoWriter(output_file, fourcc, 30, (width, height))

    frequency = 100
    count = 0

    while True:
        ret, img = vcap.read()
        if not ret:
            try:
                print("Final output: ", (x_output, y_output))
                break
            except:
                print("PID was not activated")
                break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


        if count % frequency == 0:
            #print(img.shape[0], img.shape[1]) #rows, columns
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


            y_pid = PID(0.2, 0.0, 0.0, 100)
            x_pid = PID(0.2, 0.0, 0.0, 100)

            i=1
            for tag in tags:
                print("Tag: ", i)
                center_x = sum(coord[0] for coord in tag.corners) / 4
                center_y = sum(coord[1] for coord in tag.corners) / 4
                for idx in range(len(tag.corners)):
                    cv2.line(color_img, tuple(tag.corners[idx - 1, :].astype(int)), tuple(tag.corners[idx, :].astype(int)), (0, 255, 0), 3)

                cv2.putText(color_img, str(tag.tag_id),
                            org=(tag.corners[0, 0].astype(int) + 10, tag.corners[0, 1].astype(int) + 10),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=5,
                            color=(0, 0, 255),
                            thickness =  10)
                i+=1
                #depth
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
                displaced_x = tag.center[0] - (img.shape[1]/2)
                x_output = x_pid.update(displaced_x)
                displaced_y = tag.center[1] - (img.shape[0]/2)
                y_output = y_pid.update(displaced_y)
                print((x_output, y_output))

                brov.set_vertical_power(y_output)
                brov.set_lateral_power(x_output)

                
                print((x_output, y_output))

                
            plt.imshow(color_img)
            plt.show()

        count += 1

def apriltag_detect(img, x_pid, y_pid):
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
            displaced_x = tag.center[0] - (img.shape[1]/2)
            x_output = x_pid.update(displaced_x)
            displaced_y = tag.center[1] - (img.shape[0]/2)
            y_output = y_pid.update(displaced_y)
            return((x_output, y_output))

            brov.set_vertical_power(y_output)
            brov.set_lateral_power(x_output)

        
        return((x_output, y_output))

        
        plt.imshow(color_img)
        plt.show()