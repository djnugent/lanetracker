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
        #grayscale
        if(len(frame.shape)>2):
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        #remove distortion
        #frame = cv2.undistort(frame,self.matrix,self.distortion)

        #crop
        frame = frame[180:720]

        #remap perspective
        #frame = transform(frame, self.src_corners, self.dst_corners, self.size)

        #blur the image
        #frame = cv2.blur(frame,(11,11))
        frame = cv2.GaussianBlur(frame,(3,3),0)
        #cv2.imshow("blur",frame)

        return frame

    #extract lane data from frame
    def analyze_frame(self, frame):

        #adaptive canny edge detector
        avg, null, null, null = cv2.mean(frame)
        avg = int(avg)
        edges = cv2.Canny(frame,avg/2,avg)
        edges = transform(edges, self.src_corners, self.dst_corners, self.size)



        #clean up images
        poly = np.array([[0,410],[0,639],[639,639],[639,410],[346,635],[294,635]])
        cv2.fillPoly(edges, [poly],0)
        #edges = cv2.blur(edges,(11,11))
        kernel = np.array([[0,0,1,0,0],
                            [0,0,1,0,0],
                            [0,0,1,0,0]])
        #edges = cv2.dilate(edges,kernel)
        ret, edges = cv2.threshold(edges,30,255,cv2.THRESH_BINARY)
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

        #hough probablistic line detection
        lines = cv2.HoughLinesP(edges,2,np.pi/180,2, minLineLength = 100, maxLineGap = 30)

        if lines is not None:
            lines = self.get_vertical_lines(lines,10)
            blank = np.zeros(edges.shape + (3,),np.uint8)
            for line in lines:
                pnt1,pnt2= line
                cv2.line(blank,pnt1,pnt2,(255,0,0),2)
            cv2.imshow("lines",blank)


    #filter hought lines for vertical lines
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





if __name__ == '__main__':
    detector = LaneDetector("test.mp4")
    detector.main()
