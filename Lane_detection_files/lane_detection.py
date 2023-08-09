import numpy as np
import cv2
import matplotlib.pyplot as plt
import random as rand


### ROME WROTE THE ENTIRETY OF THIS FILE
### NOT JULES OR ARTHUR!! :ANGRY_EMOTICON:

def gray(img):
    return cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

def binary_threshold(blurred_img, lower_bit_intensity = 100, upper_bit_intensity = 180):
    thresh=cv2.threshold(blurred_img, lower_bit_intensity, upper_bit_intensity, cv2.THRESH_BINARY)[1]
    return (thresh)
    
def blur(img, num):
    return cv2.medianBlur(img, num)

def detect_lines(img, threshold1=50,threshold2=150, apertureSize=3,minLineLength=100,maxLineGap=10,distance_resolution=1,Theta=np.pi/180,vote_threshold=30):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to grayscale
    edges = cv2.Canny(gray, threshold1, threshold2, apertureSize) # detect edges using edge intensity of the gray version of the image.jpg,
    #  it detects the edges by establishing a color gradient along edges and using those gradients to define thin lines where edges should be,
    #  whether or not they are edges is then defined by whether the intensity of the shift in gradient is above or below certain thresholds
    #  that you define when calling Canny, so the second value you input is defined as the minimum threshold for gradient intensity,
    #  which if any edges have an intensity lower than that they are discarded, the second threshold is the maximum intensity, 
    #  which establishes that for any edges with a greater gradient intensity they are instantly accepted as edges, 
    #  and if some edges are in-between the thresholds, they are defined as edges or not based on whether they touch pixels that are a part of the edges.
    #  for the parameters I would suggest anywhere from 55-80 to 50-110

    lines = cv2.HoughLinesP(edges,distance_resolution,Theta,vote_threshold,minLineLength,maxLineGap,) # detect lines
    # takes in edges, an array of lines mapped in cartesian space onto the image resolution
    # also takes in Rho which is distance resolution
    # then it takes in Theta which is angular pixel resolution, note: only seems to work for pi/(k*30) values, where k is some natural number, idk why
    # then it takes in a threshold for lines it will show, only lines that get more than the thresholds votes will be shown. suggest to be 10
    # then it takes in minLineLength which states the minimum length required in pixels for a line to be shown
    # then it takes in maxLineGap which states the maximum distance between two lines in points in a line for those points to be considered apart of a single line

    return (lines.tolist())

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
        for line in lines:
            if line is not None and len(line) != 0:
                x1, y1, x2, y2 = line
            (cv2.line(img, (x1, y1), (x2, y2), color, 10))
        return(img)
    
    else: print("bruh it failed")

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
                x1=line[0]
                y1=line[1]
                x2=line[2]
                y2=line[3]

                if (x2-x1)==0:
                    slope = np.power(10, 10)
                else:
                    slope=(y2-y1)/(x2-x1)

                ##MAYBE NEED CHECKER FOR IF SLOPE IS ZERO, IN WHICH CASE THAT MEANS THE LINE IS PERFECTLY VERTICAL

                slopes.append(slope)
                intercepts.append((-y1/slope)+x1)
    

            else: print("bruh it failed again again")
        
        return [slopes,intercepts] ### RETURNS LIST OF TWO LISTS
    
    else: print("bruh it failed again")

def detect_lanes(lines,s_1=1,x_1=30):
    j = 0
    k = 0 #j will grab the first line in lines and so k will just grab the second onward and we compare from there, k should equal j+1
    lanes = []
    s_n_i=get_slopes_intercepts(lines) #"slopes n interecepts"
    slopes=s_n_i[0]

    #intercepts=s_n_i[1]
def detect_lanes(lines, img):
    lanes = []

    if lines is None:
        return None
    else:
        slopes, intercepts = get_slopes_intercepts(lines)
        for i in range(len(lines)):
            for j in range(i+1, len(lines)):
                
                if (np.absolute(lines[i][0][0]-lines[j][0][0]) < 40) and (np.absolute(lines[i][0][1]-lines[j][0][1]) < 40):
                    j+=1
                    break
                if np.absolute(np.abs(slopes[i] - slopes[j])) < 0.25:
                    lanes.append([lines[i], lines[j]])
                    i += 1 #to make sure single line isn't paired with more than one other line

    return (np.array(lanes).tolist()) 
##Comparisons to add:
##Compare distance between line centers and line endpoints, should be similar for parallel lines, 
# (comment from jules)they don't need to be the same length or close to the same length i do not beleive we should add this to the programm
##Add condition for if lines are negatives of eachother, for lines that are head on to the camera
##TODO
##USE COMBINATION FUNCTION


    
    if lines is not None and len(lines)!=0:
        while j in range(len(lines)):
            k=j+1
            while k in range(len(lines)):
                if slopes is not None and slopes[j]:
                    if abs(slopes[j]-slopes[k])<s_1 and abs(lines[j][0]-lines[k][0])>x_1: #if the slopes are within 4 y pixels per x pixel and the abs_value of the x1 points for each line are within 20
                        if abs(slopes[j]+slopes[k])<2: #to check if line is head-on
                        #lanes.append([lines[j],lines[k]])
                            lanes.append([lines[j],lines[k]])
                            pass
                k+=1
            j+=1

    if lines is not None and len(lines)!=0:
        for line in lines:
            pass



    j = 0
    k = 0 
    slopes=s_n_i[0]

    # while lanes ==[]:
    #     while j in range(len(lines)):
    #         k=j+1
    #         s_1+=1
    #         x_1-=10
    #         while k in range(len(lines)):
    #             if slopes is not None and slopes[j]:
    #                 if abs(slopes[j]-slopes[k])<s_1 and abs(lines[j][0]-lines[k][0])>abs(x_1): #if the slopes are within 4 y pixels per x pixel and the abs_value of the x1 points for each line are within 20
    #                     lanes.append([lines[j],lines[k]])
    #                 if abs(slopes[j]+slopes[k])<2: #to check if line is head-on
    #                     #lanes.append([lines[j],lines[k]])
    #                     pass
    #             k+=1
    #         j+=1
    

    return(lanes)


##Rome wrote this
def get_color():
    #gets integer from 0 to 255, inclusive or not isn't really important
    c=rand.randint(0,255)
    b=rand.randint(0,255)
    a=rand.randint(0,255)
    #returns tuple you can use that 
    return((a,b,c))


##Rome
def draw_lanes(img, lanes):

    for lane in lanes:
        draw_lines(img,lane,get_color())




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

def distance(two_points):
    return(np.sqrt(abs(two_points[0][0]-two_points[0][1])**2 + abs(two_points[1][0]-two_points[1][1])**2))
    #make sure this works

def recommend_direction(centers,img):
    distances=[]
    horizontal=len(img[0])
    vertical=len(img)
    arr_centers=[] #A list of centers that is ordered by the same order of the distances, so we can refer back to the line
    for center in centers:
        d=distance(center,[horizontal/2,vertical/2])
        distances.append([d])
        arr_centers.append(center)
    
    main_point=arr_centers[distance.index((min(distances)))]

    if main_point<horizontal/2-40:
        print("Go Left!")
    if main_point>horizontal/2+40:
        print("Go Right!")
    
def half_image(image):
    return(image[int(len(image)/2):, :])


def show_images(cap,frequency):
    pass
    

def show_lines(img):
    plt.imshow(draw_lines(half_image(img),detect_lines(img)))

#if the slopes are equal or if their x1 coordinates are equally distant from the midpoint of their x2 coordinates

def show_everything(cap, frequency=150):
    try:
        a=0
        b=frequency
        ret,frame = cap.read()
        while ret:
            if a%b==0:
                plt.imshow(draw_lanes(half_image(frame),detect_lanes(my_detect_lines(frame))))
                plt.show()
               #(recommend_direction(detect_lanes(my_detect_lines(frame)), frame))
            a+=1
            ret,frame = cap.read()
    except TypeError or IndexError:
        a=0
        b=60
        ret,frame = cap.read()
        while ret:
           if a%b==0:
               plt.imshow(draw_lanes(half_image(frame),detect_lanes(my_detect_lines(frame))))
               plt.show()
           a+=1
           ret,frame = cap.read()

def show_lanes(img):
    plt.imshow(draw_lanes(detect_lanes(detect_lines(img))))
    return(plt.show())


def line_checker(lines):
    if lines is not None:
        for line in lines:
            if line is not None and len(line) != 0:
                print(line)
    print(lines[0])
    print(lines[1])
    print(lines[0][0])
    print(lines[0][0][0])
    print("full lines list:")
    print(lines)