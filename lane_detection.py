import cv2
import numpy as np
import matplotlib.pyplot as plt
import random as rand


def gray(img):
    return cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

def binary_threshold(blurred_img, lower_bit_intensity = 100, upper_bit_intensity = 180):
    thresh=cv2.threshold(blurred_img, lower_bit_intensity, upper_bit_intensity, cv2.THRESH_BINARY)[1]
    return (thresh)
    
def blur(img, num):
    return cv2.medianBlur(img, num)


def my_detect_lines(img):
    #gray = cv2.medianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),41) # convert to grayscale

    new_gray = gray(img) # SHOULD RETURN NP ARRAY

    blur = blur(new_gray, 41) # SHOULD RETURN NP ARRAY

    thresh = binary_threshold(blur)# SHOULD BE NP ARRAY

    new_thresh = thresh[int(len(thresh)/2):, :] ### CODE DOES WORK, Dr.Saad WROTE

    edges = cv2.Canny(new_thresh, 35, 67) 

    ###NOTE
    # detect edges using edge intensity of the gray version of the image.jpg,
    #  it detects the edges by establishing a color gradient along edges and using those gradients to define thin lines where edges should be,
    #  whether or not they are edges is then defined by whether the intensity of the shift in gradient is above or below certain thresholds
    #  that you define when calling Canny, so the second value you input is defined as the minimum threshold for gradient intensity,
    #  which if any edges have an intensity lower than that they are discarded, the second threshold is the maximum intensity, 
    #  which establishes that for any edges with a greater gradient intensity they are instantly accepted as edges, 
    #  and if some edges are in-between the thresholds, they are defined as edges or not based on whether they touch pixels that are a part of the edges.
    #  for the parameters I would suggest anywhere from 55-80 to 50-110
    ###NOTE

    lines=[]
    
    bad_lines = cv2.HoughLinesP(edges,4,np.pi/120,30,minLineLength=250,maxLineGap=50,) # detect lines, 10, np.pi/210,50,250,20

    # takes in edges, an array of lines mapped in cartesian space onto the image resolution
    # also takes in Rho which is distance resolution
    # then it takes in Theta which is angular pixel resolution, note: only seems to work for pi/(k*30) values, where k is some natural number, idk why
    # then it takes in a threshold for lines it will show, only lines that get more than the thresholds votes will be shown. suggest to be 10
    # then it takes in minLineLength which states the minimum length required in pixels for a line to be shown
    # then it takes in maxLineGap which states the maximum distance between two lines in points in a line for those points to be considered apart of a single line
    ##BAD LINES== [ [[LINE I WANT]], [[OTHER LINE I WANT]]]


    try:
        if bad_lines is not None:
            for nested1 in bad_lines:
                    nested=nested1[0]
                    lines.append(nested.tolist())
            return(lines) #AS LIST of LIST CONTAINING TWO POINTS EX: [[x1,y1,x2,y2],[x1,y1,x2,y2]]
        
    except TypeError:
        #raise ValueError("No Lines!")
        return None

def draw_lines(img,lines,color=(0,255,0)):
    #These are checks for if lines is real, if each line in lines is real, and if each line is not an empty set
    # if lines is not None:
    #     if lines[0] is int:
    #         x1,y1,x2,y2=lines
    #         if (x2-x1)!=0:
    #             pass
    #         elif (x2-x1)==0:
    #             x2+=.1
    #         (cv2.line(img, (x1, y1), (x2, y2), color, 10))
        # else:
    if lines is not None and len(lines) != 0:
        if lines[0] is int:
            for line in lines:
                if line is not None and len(line) != 0:
                    x1, y1, x2, y2 = line
                (cv2.line(img, (x1, y1), (x2, y2), color, 10))
            return(img)
        else:
            return(img)
    else: 
        return(img)

def get_slopes_intercepts(lines):
    slopes=[]
    intercepts=[]
    #easy_return_value=[]
    slope=0
    ###NOTE
    ###LINES SHOULD BE IN THIS FORM
    ###LINES = [[x1,y1,x2,y2],[x1,y1,x2,y2]...]


    if lines is not None and len(lines) != 0:
        for line in lines:
            if line is not None and len(line) != 0:
                if line[0] is int:
                    x1=line[0]
                    y1=line[1]
                    x2=line[2]
                    y2=line[3]


                    if (x2-x1)==0:
                        slope = np.power(10, 10)
                    else:
                        slope=(y2-y1)/(x2-x1)

                    ##MAYBE NEED CHECKER FOR IF SLOPE IS ZERO, IN WHICH CASE THAT MEANS THE LINE IS PERFECTLY VERTICAL
                    intercept=(-y1/slope)+x1
                    slopes.append(slope)
                    intercepts.append(intercept)
                else:
                    break
            else: 
                break
            
            return [slopes,intercepts] ### RETURNS LIST OF TWO LISTS
    
    else: 
        return [[], []]

def get_color():
    c=rand.randint(0,255)
    b=rand.randint(0,255)
    a=rand.randint(0,255)
    return((a,b,c))

def detect_lanes(lines, img):
    lanes = []

    if lines is None:
        return None
    else:
        slopes, intercepts = get_slopes_intercepts(lines)
        for i in range(len(lines)):
            if lines[i][0][3] > len(img):
                pass
            else:
                for j in range(i+1, len(lines)):
                    
                    if (np.absolute(lines[i][0][0]-lines[j][0][0]) < 40) and (np.absolute(lines[i][0][1]-lines[j][0][1]) < 40):
                        j+=1
                        break
                    if np.absolute(np.abs(slopes[i] - slopes[j])) < 0.25:
                        lanes.append([lines[i], lines[j]])
                        i += 1 #to make sure single line isn't paired with more than one other line

    return (np.array(lanes).tolist()) 


def draw_lanes(image, lanes):
    if lanes is None:
        pass
    else:
        for lane in lanes:
            color = get_color()
            draw_lines(image, lane, color)
    return image



def get_lane_center(lanes):
    ##get_slopes_intercepts returns the slope and intercept in a tuple, lanes[0][0] gets the first line in the first lane
    x_avg=[]
    y_avg=[]
    centers=[]
    for lane in lanes:
        x_avg=[]
        y_avg=[]
        for line in lane:
            x_avg.append((line[0]+line[2])/2)
            y_avg.append((line[1]+line[3])/2)
        x_favg=(x_avg[0]+x_avg[1])/2
        y_favg=(y_avg[0]+y_avg[1])/2
        centers.append([x_favg,y_favg])

    return(centers)

def recommend_direction(center, img):
    if center is None:
        pass
    else:
        #Gets if center is within 10 pixels of 960, it returns forward, otherwise gets back to center
        if center< len(img[0]-10):
            return("left")
        elif center>len(img[0]+10):
            return("right")
        elif center <970 and center>950:
            return("forward")

def recommend_turn(slope):

    if np.abs(slope) > 3:
        return "don't turn"
    elif slope > -3 and slope < 0:
        return "turn right"
    else:
        return "turn left"

def get_distance_from_lane(lane_center = [0, 0], img = 5):
    if img == 5:
        return 0
    else:
        img_center = len(img)[1]/2
        d = np.abs(img-lane_center[0])
        return d
