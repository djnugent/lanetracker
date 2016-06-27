import time
import cv2
import numpy as np
import math
from helpers import *



class LaneDetector():

    def __init__(self,source):
        self.source = source
        #perspective mapping characteristics
        self.size = 640,640
        self.src_corners = np.float32([[0,719],[1279,719],[400,0],[880,0]])
        self.dst_corners = np.float32([[300,self.size[1]],[self.size[0]-300,self.size[1]],[0,0],[self.size[0],0]])

        #distortion characteristics
        self.matrix = np.array([[764.36600634, 0.0, 663.58169499],
        	[0.0, 764.86442335, 363.45071788],
        	[0.0, 0.0, 1.0]])
        self.distortion = np.array([-0.29435659, 0.14030301, 0.0, 0.0, 0.0])


        self.frames_since_last_detect = 4
        self.area_thresh = 100000

    def main(self):
        #open camera/video
        vid = cv2.VideoCapture(self.source)
        if vid is None:
            print "unable to open video"
            return

        while True:
            ret, frame = vid.read()
            if frame is None:
                print "failed to grab frame"
                continue


            processed = self.analyze_frame(frame)
            cv2.waitKey(1)



    def analyze_frame(self,frame):

        #remove distortion
        #frame = cv2.undistort(frame,self.matrix,self.distortion)

        #crop
        frame = frame[180:720]

        #remap perspective
        frame = transform(frame, self.src_corners, self.dst_corners, self.size)
        draw = np.copy(frame)

        #hsv color space
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame = cv2.split(frame)[1]

        threshold = self.calculate_lane_threshold(frame,1.8)

        ret,frame = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)
        kernel = np.ones((3,3),dtype=np.uint8)
        frame = cv2.erode(frame,kernel,iterations = 1)

        poly = np.array([[0,300],[0,639],[639,639],[639,300],[340,635],[300,635]])
        cv2.fillPoly(frame, [poly],0)

        left_line, center_line, right_line = self.find_lane(frame)
        for pnt in left_line:
            cv2.circle(draw,pnt,5,(255,0,0),-1)
        for pnt in center_line:
            cv2.circle(draw,pnt,5,(255,255,0),-1)
        for pnt in right_line:
            cv2.circle(draw,pnt,5,(0,0,255),-1)

        cv2.imshow("lane",draw)

        return frame



    #determine lane color bounds based on a ROI
    def calculate_lane_threshold(self,frame,scalar):
        roi = frame[400:620,280:360]
        median = np.percentile(roi,50)
        return median * scalar

    def find_lane(self,frame):
        w,h = frame.shape

        #parameters
        starting_y = 580                #what y pixel we start looking for the lane
        step_y = 25                     #how many pixel we step between scans
        line_threshold = 127            #what pixel value is considered an edge
        max_lane_width = 200            #when we stop classifying the edge as a lane
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







if __name__ == '__main__':
    detector = LaneDetector("test.mp4")
    detector.main()
