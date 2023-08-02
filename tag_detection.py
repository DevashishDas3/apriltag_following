from dt_apriltags import Detector
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pid
import numpy as np
from math import isclose

class TD:

    def __init__(self):
        self.at_detector = Detector(families='tag36h11',
                    nthreads=1,
                    quad_decimate=1.0,
                    quad_sigma=0.0,
                    refine_edges=1,
                    decode_sharpening=0.25,
                    debug=0)

        self.cameraMatrix = np.array([ 1060.71, 0, 960, 0, 1060.71, 540, 0, 0, 1]).reshape((3,3))
        self.camera_params = ( self.cameraMatrix[0,0], self.cameraMatrix[1,1], self.cameraMatrix[0,2], self.cameraMatrix[1,2] )
        #self.img=img

    def detect_tags(self, img):
        return self.at_detector.detect(img, True, self.camera_params, tag_size  = 0.1)

    def get_video(self, src="AprilTagTest.mkv"):
        vcap=cv2.VideoCapture(src)
        return(vcap)

    ### NEEDS TESTING TO SEE IF vcap.read()[1] WORKS
    def get_frame(self, vcap):
        frame = vcap.read()[1] #Should return that frame is vcap.read()[1] on the basis that ret,frame = vcap.read() works
        return(frame)

    def make_gray(self, frame):
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) # convert to grayscale
        return gray




    # def detect_tags(gray):

        

        
        
    #     ##NOTE
    #     ##TAGS IS RETURNED AS A LIST OF DETECTION OBJECTS
    #     ##EACH DETECTION OBJECT HAS MEMBER VARIABLES LIKE CENTER, CORNERS, AND SO ON
    #     ##TO GRAB THE CENTER WE NEED TO USE, tags[0] WHICH GRABS THE FIRST TAG THAT IS SEEN IN TAGS
    #     ##THEN ONTO THAT WE ADD .Center WHICH GETS THE CENTER MEMBER VARIABLE OF THAT DETECTION OBJECT
    #     ##THAT COMES OUT AS A NP ARRAY, SO IF WE WANT TO USE EACH VALUE IN THAT CENTER ARRAY, IT MIGHT BE EASIER TO DO .tolist()
    #     ##NOTE
        
    #     if tags is not None:
    #         return tags
    #     else:
    #         pass

    #     #raise ValueError


    def get_centers_from_tags(self, tags):
        center_list=[]
        for tag in tags:
            center_list.append(tag.center.tolist())
        return(center_list)




    def get_center(self, img):
        # gets the center of image as a tuple 
        #or literally "return img.center" lol one line
        vertical = len(img)
        horizontal = len(img[0]) 
        return horizontal/2, vertical/2

    def get_distance(self, point1, point2):
        # returns distance of two points x, y
        return (point1[0] - point2[0]), (point1[1] - point2[1])

    def get_distance_from_center(self, img, point):
        return self.get_distance(point, self.get_center(img))

    def get_percentage(self, img, H_d, V_d):
        
        return H_d/len(img[0]), V_d/len(img)
        
    def draw_line(self, img, lines, color=(255,0,0), thickness=10):
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

    def half_image(self, img):
        # returns half image
        halfimg = img[img.shape[0]/2:img.shape[1]]
        return halfimg

    def draw_line_center(self, img, tag, color=(255,0,0),thickness=10):
        #draws line from center to tag
        center= self.get_center(img)
        cv2.draw_line(img,center, tuple(map(int(tag.center))),color,thickness)
        
        #cv2.line(img, tuple(map(int, tag.center)), tuple(map(int, np.array(img.shape[1::-1])/2)), (255, 0, 0), 3)

    def return_PID_values(self, img, tag, pid_horizontal: pid.PID, pid_vertical: pid.PID):
        # takes in img, tag (the first tag), two PIDs to send final control signals
        print(img[0])
        horizontal_error = tag.center[0] - self.get_center(img)[0]
        vertical_error = tag.center[1] - self.get_center(img)[1]
        
        x_output = pid_horizontal.update(horizontal_error)
        y_output = pid_vertical.update(vertical_error)

        return x_output, y_output



    ##Arthur Wrote
    def interruption(self, img):
        cv2.imread(img)
        ret, frame= cv2.read()

        while ret: #if key q is pressed interrupt
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    




    # def main():

    #     vcap=get_video("AprilTagTest.mkv")
    #     ret, frame = vcap.read()

    #     ##Need to fix the while ret to make it work
        
    #     while ret:
    #         try:
    #             ##TODO GET IMAGE FROM VIDEO USING GET FRAME
    #             frame = get_frame(vcap)
                
    #             ##TODO MAKE THAT FRAME GRAYSCALE
    #             gray = make_gray(frame)

    #             ##TODO DETECT TAGS IN THAT GRAY IMAGE USING GRAYSCALE OUTPUT
    #             tags = detect_tags(gray)

    #             ##TODO GET DISTANCE FROM CENTER OF APRIL TAG TO CENTER OF CAMERA USING CAMERA RESOLUTION AND APRILTAG LOCATION
    #             distance_tuple = get_distance_from_center(frame, tags[0])  ##ERROR IS THAT IT TAKES IN DETECTION OBJECTS RATHER THAN POINTS FOR GET DISTANCE

    #             ##TODO DRAW LINE TO CENTER OF APRIL TAG
    #             draw_line_center(frame, tags[0])

    #             ##TODO GET PERCENTAGES FOR EACH COMPONENT
    #             percentage_pair = get_percentage(frame,distance_tuple[0],distance_tuple[1])
                
    #             ##TODO DRAW COMPONENT LINES AND  THEIR VALUES:
                

    #             ##TODO GET X AND Y VALUES
                
    #             ##TODO PUT X_DISTANCE AND Y_DISTANCE INTO PID AND TAKE OUTPUT
    #             tag_list = detect_tags(gray)
    #             center_list = get_centers_from_tags(tag_list)
    #             x_distance, y_distance = get_distance_from_center(frame, center_list[0])
        
    #             ##TODO GET THAT OUTPUT AND SEND IT INTO TO MAV CONTROLS

    #             lateral_power, vertical_power = send_PID_control(frame, tags[0], x_distance, y_distance) #WRONG CODE SUCKS ASS



    #             print(f"Lateral Power: {lateral_power}\nVertical Power: {vertical_power} \n it might have moved")
                
    #             ret, frame= vcap.read()
                

    #         ##TODO MAKE THIS A LOOP USING TRY AND EXCEPT FOR KEYBOARD INTERRUPT

    #         except KeyboardInterrupt:
    #             print("Closed reader")
                


    # if __name__ == "__main__":
    #     main()


    
    