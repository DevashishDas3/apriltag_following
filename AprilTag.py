import numpy as np



def analyze_tags(img, gray):
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
            tag_x, tag_y = tag.center

            for idx in range(len(tag.corners)):
                cv2.line(color_img, tuple(tag.corners[idx - 1, :].astype(int)), tuple(tag.corners[idx, :].astype(int)), (255, 0, 0), 3)

            cv2.putText(color_img, "Tag ID: #" + str(tag.tag_id),
                        org=(1400, 1000),
                        fontFace=cv2.FONT_HERSHEY_DUPLEX,
                        fontScale=3,
                        color=(0, 0, 255),
                        thickness =  10)
            i+=1
            #depth

            print(tag.corners[0, 0].astype(int) + 10, tag.corners[0, 1].astype(int) + 10)

            
            rows, columns, channels = color_img.shape
            print(color_img.shape)
            horizontal_difference = 0
            vertical_difference = 0

            #horizontal (percentage)
            if tag.center[0] <= columns/2:
                horizontal_difference = tag.center[0] - columns/2
                p_horizontal_difference = horizontal_difference
                p_horizontal_difference = abs(np.round((horizontal_difference/(columns)) *  100, 2))
                cv2.putText(color_img, str(p_horizontal_difference) + "%" + " of hor",
                                    #org=(int(columns/2 - horizontal_difference/2 - 100), int(rows/2)),
                                    org=(int(tag_x), int(rows/2)),
                                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                                    fontScale=2,
                                    color=(205, 92, 92),
                                    thickness = 8)
            else:
                horizontal_difference = tag.center[0] - columns/2
                p_horizontal_difference = horizontal_difference
                p_horizontal_difference = abs(np.round((horizontal_difference/(columns)) *  100, 2))
                cv2.putText(color_img, str(p_horizontal_difference) + "%" + " of hor",
                                    #org=(int(columns/2 + horizontal_difference/2 + 100), int(rows/2)),
                                    org=(int(tag_x), int(rows/2)),
                                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                                    fontScale=2,
                                    color=(205, 92, 92),
                                    thickness = 8)

            

            print("percent: " + str(p_horizontal_difference))

            
            #cv2.line(color_img, (columns/2, rows/2), (columns/2) + horizontal_difference, rows/2), (255, 0, 0), 3)
        

            #vertical (percentage)
            if tag.center[0] <= rows/2:
                vertical_difference = rows/2 + tag.center[1]
                p_vertical_difference = vertical_difference
                p_vertical_difference = abs(np.round((vertical_difference/(rows)) *  100, 2))

                cv2.putText(color_img, str(p_vertical_difference) + "%" + " of vert",
                                        #org=(int(columns/2), int(rows/2 + vertical_difference/2 - 200)),
                                        org=(int(tag_x), int(tag_y)),
                                        fontFace=cv2.FONT_HERSHEY_DUPLEX,
                                        fontScale=2,
                                        color=(205, 92, 92),
                                        thickness = 8)
            else:
                vertical_difference = tag.center[1] - rows/2
                p_vertical_difference = vertical_difference
                p_vertical_difference = abs(np.round((vertical_difference/(rows)) *  100, 2))

                cv2.putText(color_img, str(p_vertical_difference) + "%" + " of vert",
                                        #org=(int(columns/2), int(rows/2 + vertical_difference/2 - 100)),
                                        org=(int(tag_x), int(tag_y)),
                                        fontFace=cv2.FONT_HERSHEY_DUPLEX,
                                        fontScale=2,
                                        color=(205, 92, 92),
                                        thickness = 8)
            

            print("percent: " + str(p_vertical_difference))
            
            #cv2.line(color_img, (columns/2, rows/2), (columns/2, rows/2 + vertical_difference), (255, 0, 0), 3)

            
            
            #hypotenuse (display pixel length)

            print("Tag Coords: ")
            print(str(int(tag_x)))
            print(str(int(tag_y)))
            print(columns/2)
            print(rows/2)

            cv2.line(color_img, tuple(map(int, tag.center)), tuple(map(int, np.array(img.shape[1::-1])/2)), (255, 0, 0), 6)


            hypotenuse = np.sqrt(pow((tag.center[0] - columns/2), 2) + pow((tag.center[1] - rows/2), 2))
            cv2.putText(color_img, "hyp: " + str(int(hypotenuse)) + "px",
                                    org=(int(columns/2), int((tag_y + rows/2)/2)),
                                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                                    fontScale=2,
                                    color=(205, 92, 92),
                                    thickness = 8)
            
            cv2.line(color_img, (int(columns/2), int(rows/2)), (int(tag_x), int(rows/2)), (255, 0, 0), 6)
            cv2.line(color_img, (int(tag_x), int(rows/2)), (int(tag_x), int(tag_y)), (255, 0, 0), 6)

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
