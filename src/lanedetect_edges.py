import time
import cv2
import numpy as np
import math
from helpers import *

'''
lanedetect_edges.py - Detects lane using canny edge detection. Wish it worked better due to it's
                    versatility in varying lighting conditions, but it gets confused by highly
                    textured environments. Currently executes on a static file "test.mp4"

parameters  - video source: currently test.mp4
            - perspective mapping characteristics: Have to be hard coded if the camera's FOV, angle, height, or image size changed
                * This is a trial and error process for your video source
            - distortion characteristics: Currently not used but can be calculated using openCV


usage - python lanedetect_edges.py
'''

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


    #extract lane data from frame
    def analyze_frame(self, frame):
        #grayscale
        if(len(frame.shape)>2):
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        #remove distortion
        #frame = cv2.undistort(frame,self.matrix,self.distortion)

        #crop
        frame = frame[180:720]

        #remap perspective
        draw = transform(frame, self.src_corners, self.dst_corners, self.size)

        #blur the image
        frame = cv2.GaussianBlur(frame,(3,3),0)


        #adaptive canny edge detector
        avg, null, null, null = cv2.mean(frame)
        avg = int(avg)
        edges = cv2.Canny(frame,avg/2,avg)
        edges = transform(edges, self.src_corners, self.dst_corners, self.size)

        #clean up images
        poly = np.array([[0,300],[0,639],[639,639],[639,300],[340,635],[300,635]])
        cv2.fillPoly(edges, [poly],0)
        '''
        kernel = np.array([[0,0,1,0,0],
                            [0,0,1,0,0],
                            [0,0,1,0,0]])
        #edges = cv2.dilate(edges,kernel)
        ret, edges = cv2.threshold(edges,30,255,cv2.THRESH_BINARY)
        '''
        cv2.imshow("edges", edges)


        '''
        #findContours
        im2, contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        filled = np.zeros(edges.shape,np.uint8)
        cv2.drawContours(filled, contours, -1, 255, -1)
        #filled = transform(filled, self.src_corners, self.dst_corners, self.size)
        cv2.imshow("filled",filled)
        '''

        '''
        #thining
        skel = thin(edges)
        cv2.imshow("thin",skel)
        '''

        left_line, center_line, right_line = find_lane(edges)
        for pnt in left_line:
            cv2.circle(draw,pnt,5,(255,0,0),-1)
        for pnt in center_line:
            cv2.circle(draw,pnt,5,(255,255,0),-1)
        for pnt in right_line:
            cv2.circle(draw,pnt,5,(0,0,255),-1)

        cv2.imshow("lane",draw)

        return frame



if __name__ == '__main__':
    detector = LaneDetector("../test.mp4")
    detector.main()
