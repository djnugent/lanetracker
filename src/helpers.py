import cv2
import numpy as np

'''
helpers.py - general CV helper functions
'''

def transform(img,src_corners,dst_corners,size):
    #project image
    M = cv2.getPerspectiveTransform(src_corners,dst_corners)
    per = cv2.warpPerspective(img,M,size,borderValue=255)
    return per

def thin(img):
    size = np.size(img)
    skel = np.zeros(img.shape,np.uint8)

    ret,img = cv2.threshold(img,127,255,0)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    done = False

    while( not done):
        eroded = cv2.erode(img,element)
        temp = cv2.dilate(eroded,element)
        temp = cv2.subtract(img,temp)
        skel = cv2.bitwise_or(skel,temp)
        img = eroded.copy()

        zeros = size - cv2.countNonZero(img)
        if zeros==size:
            done = True
    return skel

def balance(orig,min_range,res_reduction):

    img = np.copy(orig)
    #get min, max and range of image
    min_v = np.percentile(img,5)
    max_v = np.percentile(img,95)

    #clip extremes
    img.clip(min_v,max_v, img)

    #scale image so that brightest pixel is 255 and darkest is 0
    range_v = max_v - min_v
    if(range_v > min_range):
        img -= int(min_v)
        img *= int(255.0/(range_v))
        '''
        img /= res_reduction
        img *= res_reduction
        '''
        return img
    else:
        return np.zeros((img.shape[0],img.shape[1]), np.uint8)

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged


def find_lane(frame):
    w,h = frame.shape

    #parameters
    starting_y = 580                #what y pixel we start looking for the lane
    step_y = 25                     #how many pixel we step between scans
    line_threshold = 127            #what pixel value is considered an edge
    max_lane_width = 150            #when we stop classifying the edge as a lane
    max_lane_divergence = 15        #how aggressively the lane can change direction

    #lane data
    left_line = []
    right_line = []
    center_line = []


    current_y = starting_y + 3
    while True:
        #use previous lane center as X starting point - if it exists
        if len(center_line) > 0:
            center_x = center_line[-1][0]
        else:
            center_x = w/2
        #move up the image
        current_y  -= step_y

        #check for lane end or image end
        if current_y < 0 or frame[current_y][center_x] > line_threshold:
            break

        #if lane hasn't ended scan left
        cnt = 0
        found_left_line = False
        left_x = 0
        while not found_left_line and cnt < max_lane_width:
            left_x = center_x - cnt
            if left_x < 0: #we hit the image border so we can't extract line data
                break
            pixel = frame[current_y][left_x]
            if pixel > line_threshold: #white pixel
                found_left_line = True
            cnt+=1

        #if lane hasn't ended scan right
        cnt = 0
        found_right_line = False
        right_x = 0
        while not found_right_line and cnt < max_lane_width:
            right_x = center_x + cnt
            if right_x > w - 1: #we hit the image border so we can't extract line data
                break
            pixel = frame[current_y][right_x]
            if pixel > line_threshold: #white pixel
                found_right_line = True
            cnt+=1



        #check for line divergance
        if found_left_line and len(left_line)>0:
            last_left_line = left_line[-1]
            diff_left = abs(left_x - last_left_line[0])
            if diff_left > max_lane_divergence:
                found_left_line = False
        if found_right_line and len(right_line)>0:
            last_right_line = right_line[-1]
            diff_right = abs(right_x - last_right_line[0])
            if diff_right > max_lane_divergence:
                found_right_line = False


        #both lines found
        if found_left_line and found_right_line:
            lane_width = right_x - left_x
            #lane is not too wide - calculate new center an check line divergance
            if lane_width <= max_lane_width:
                center_x = (left_x + right_x)/2

                right_line.append((right_x,current_y))
                left_line.append((left_x,current_y))
                center_line.append((center_x,current_y))

        #only found left line - try to calculate center using existing lane data
        elif found_left_line:
            if len(left_line) > 0 and len(center_line) > 0:
                last_left_line = left_line[-1]
                last_center_line = center_line[-1]
                diff = last_center_line[0] - last_left_line[0]
                center_x = left_x + diff
                center_line.append((center_x,current_y))
            left_line.append((left_x,current_y))

        #only found right line - try to calculate center
        elif found_right_line:
            if len(right_line) > 0 and len(center_line) > 0:
                last_right_line = right_line[-1]
                last_center_line = center_line[-1]
                diff = last_center_line[0] - last_right_line[0]
                center_x = right_x + diff
                center_line.append((center_x,current_y))
            right_line.append((right_x,current_y))

    return (left_line, center_line, right_line)
