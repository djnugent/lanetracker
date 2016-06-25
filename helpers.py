import cv2
import numpy as np



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
