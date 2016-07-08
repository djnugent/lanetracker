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
            cv2.imshow("original",frame)
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

        left_line, center_line, right_line = find_lane(frame)
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







if __name__ == '__main__':
    detector = LaneDetector("test.mp4")
    detector.main()
