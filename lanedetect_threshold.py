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

            #undistort, crop, fix image
            processed = self.preprocess(frame)
            cv2.imshow("processed", processed)
            #extract useful data
            data = self.analyze_frame(processed)

            cv2.waitKey(1)

    #clean up and process image before attempting to extract data
    def preprocess(self,frame):

        #crop
        frame = frame[180:720]

        #remove distortion
        #frame = cv2.undistort(frame,self.matrix,self.distortion)

        #hsv color space
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #remap perspective
        frame = transform(frame, self.src_corners, self.dst_corners, self.size)

        #blur
        frame = cv2.blur(frame,(11,11))
        cv2.imshow("perspective",frame)


        #threshold
        #use last frame threshold if we got a lock
        if self.frames_since_last_detect == 0:
            self.threshold = self.last_threshold
        #rethreshold if we haven't gotten a lock in a few frames
        elif self.frames_since_last_detect > 3:
            self.threshold = self.calculate_lane_threshold(frame)
            self.last_threshold = self.threshold

        frame = cv2.inRange(frame,self.threshold[0],self.threshold[1])

        return frame


    #extract lane data from frame
    def analyze_frame(self, frame):

        #findContours
        im2, contours, hierarchy = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        lane = np.zeros(frame.shape + (3,),np.uint8)

        #find largest contour
        largest_per = 0
        largest = None
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
            per = cv2.arcLength(approx,True)
            if per > largest_per:
                largest_per = per
                largest = approx

        #bounding rectangle
        rect = cv2.minAreaRect(largest)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(lane,[box],0,(255,0,0),2)

        (x,y),(w,h),theta = rect
        if theta < -60:
            temp = w
            w = h
            h = temp
            theta += 90
        #check for a "lane like" contour
        if w > 220 or w < 100 or h < 500 or abs(theta) > 16:
            #not a lane - color it red
            self.frames_since_last_detect +=1
            cv2.drawContours(lane, [largest], -1, (0,0,255), -1)
        else:
            #could be a lane color is green
            self.frames_since_last_detect = 0
            cv2.drawContours(lane, [largest], -1, (0,255,0), -1)

        cv2.imshow("lane",lane)


        '''
        #hough line detection
        lines = cv2.HoughLines(edges,1,np.pi/180,400)
        blank = np.zeros(edges.shape + (3,),np.uint8)
        if lines is not None:
            for (rho,theta), in lines:

                if math.degrees(theta) > 85 or math.degrees(theta) < 95:
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a*rho
                    y0 = b*rho
                    x1 = int(x0 + 1200*(-b))   # Here i have used int() instead of rounding the decimal value, so 3.8 --> 3
                    y1 = int(y0 + 1200*(a))    # But if you want to round the number, then use np.around() function, then 3.8 --> 4.0
                    x2 = int(x0 - 1200*(-b))   # But we need integers, so use int() function after that, ie int(np.around(x))
                    y2 = int(y0 - 1200*(a))
                    cv2.line(blank,(x1,y1),(x2,y2),(0,255,0),2)
        cv2.imshow('houghlines',blank)
        '''
        '''
        #hough probablistic line detection
        lines = cv2.HoughLinesP(edges,2,np.pi/180,2, minLineLength = 100, maxLineGap = 30)

        if lines is not None:
            lines = self.get_vertical_lines(lines,10)
            blank = np.zeros(edges.shape + (3,),np.uint8)
            for line in lines:
                pnt1,pnt2= line
                cv2.line(blank,pnt1,pnt2,(255,0,0),2)
            cv2.imshow("lines",blank)
        '''


    #filter hought lines for vertical lines - not used
    def get_vertical_lines(self, lines, angle_threshold):
        vertical_lines = []
        for line in lines:
            x1,y1,x2,y2 = line[0]

            angle = math.degrees(math.atan2((y1-y2),(x1-x2)))
            #first and second quadrant
            if angle > 180:
                angle = (angle + 180) % 360
            if angle < 0:
                angle = angle + 180
            #shift left 90 degrees
            angle -= 90
            if angle > -angle_threshold and angle < angle_threshold:
                if y1 > y2:
                    vertical_lines.append([(x1,y1),(x2,y2)])
                else:
                    vertical_lines.append([(x2,y2),(x1,y1)])
        return vertical_lines


    #determine lane color bounds based on a ROI
    def calculate_lane_threshold(self,frame):
        roi = frame[0:640,280:360]

        #calculate max and min
        flat = np.reshape(roi, (-1, roi.shape[-1]))
        min_hsv = np.percentile(flat,5,axis = 0)
        max_hsv = np.percentile(flat,95,axis = 0)
        return min_hsv,max_hsv




if __name__ == '__main__':
    detector = LaneDetector("test.mp4")
    detector.main()
