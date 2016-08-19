import json
import math
import cv2
import numpy as np
from map import Mapbox
from dronekit import Command
from dronekit import LocationGlobalRelative as Location

# Reads classic wpl110 mission files(mission planner)
def read_mission_wpl110(file_stream):
    missionlist=[]
    file_stream.seek(0)
    for i, line in enumerate(file_stream):
        if i==0:
            if not line.startswith('QGC WPL 110'):
                raise Exception('File is not supported WP version')
        else:
            linearray=line.split('\t')
            ln_index=int(linearray[0])
            ln_currentwp=int(linearray[1])
            ln_frame=int(linearray[2])
            ln_command=int(linearray[3])
            ln_param1=float(linearray[4])
            ln_param2=float(linearray[5])
            ln_param3=float(linearray[6])
            ln_param4=float(linearray[7])
            ln_param5=float(linearray[8])
            ln_param6=float(linearray[9])
            ln_param7=float(linearray[10])
            ln_autocontinue=int(linearray[11].strip())
            cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
            missionlist.append(cmd)
    return missionlist

# Reads qgroundcontrol json mission file
def read_mission_json(file_stream):
    missionlist=[]
    file_stream.seek(0)
    data = json.load(file_stream)
    for i, item in enumerate(data["items"]):
        ln_index = int(item["id"])
        if i == 0:
            ln_currentwp = 1
        else:
            ln_currentwp = 0
        ln_frame = int(item["frame"])
        ln_command = int(item["command"])
        ln_param1 = float(item["param1"])
        ln_param2 = float(item["param2"])
        ln_param3 = float(item["param3"])
        ln_param4 = float(item["param4"])
        ln_param5 = float(item["coordinate"][0])
        ln_param6 = float(item["coordinate"][1])
        ln_param7 = float(item["coordinate"][2])
        ln_autocontinue = int(item["autoContinue"])
        cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
        missionlist.append(cmd)
    return missionlist

# reads a mission file
def read_mission(aFileName):
    #cmds = vehicle.commands
    with open(aFileName) as f:
        if f.readline().startswith('QGC WPL 110'):
            return read_mission_wpl110(f)
        else:
            return read_mission_json(f)

# extracts Waypoints from mission file
def mission_to_locations(mission):
    locations  = []
    for cmd in mission:
        if cmd.command == 16: #waypoint
            locations.append(Location(cmd.x,cmd.y,cmd.z))
    return locations

# locates a lane in map image
def find_lane_placement(img):
    w,h,c = img.shape
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img = cv2.split(img)[1]
    img = cv2.blur(img,(21,21))
    threshold = img[w/2][h/2]/1.8
    ret,img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    kernel = np.ones((31,31),dtype=np.uint8)
    img = cv2.dilate(img,kernel)
    img = cv2.erode(img,kernel,iterations = 1)


    smallest_index = 0
    smallest_diameter = 99999
    smallest_left = 0
    smallest_right = 0
    for deg in range(0,360):
        #find left lane
        pixel = 255
        left_radius = 1
        while pixel == 255 and left_radius < w/2 and left_radius< h/2:
            x = w/2 + left_radius * math.cos(math.radians(deg))
            y = h/2 - left_radius * math.sin(math.radians(deg))
            pixel = img[y][x]
            left_radius += 5

        #find right lane
        pixel = 255
        right_radius = 1
        while pixel == 255 and right_radius < w/2 and right_radius< h/2:
            x = w/2 - right_radius * math.cos(math.radians(deg))
            y = h/2 + right_radius * math.sin(math.radians(deg))
            pixel = img[y][x]
            right_radius += 5

        diameter = left_radius + right_radius
        if diameter < smallest_diameter:
            smallest_diameter = diameter
            smallest_index = deg
            smallest_left = left_radius
            smallest_right = right_radius

    return smallest_index, smallest_left, smallest_right


if __name__ == '__main__':

    mapbox = Mapbox(username = 'djnugent', style_id = 'cirwqwpwc001sgwkoo9nok0l2')

    mission_list = read_mission("thunderhill.mission")

    print "Loaded {} waypoints".format(len(mission_list))

    for wp in mission_list:
        code, img = mapbox.static_image(lat=wp.x,lon=wp.y,zoom=20)
        if code == 200:
            draw = np.copy(img)
            w,h,c = img.shape

            #extract lane data and draw it
            deg, left_rad, right_rad = find_lane_placement(img)
            lx = int(w/2 + left_rad*math.cos(math.radians(deg)))
            ly = int(h/2 - left_rad*math.sin(math.radians(deg)))
            rx = int(w/2 - right_rad*math.cos(math.radians(deg)))
            ry = int(h/2 + right_rad*math.sin(math.radians(deg)))

            cv2.circle(draw,(lx,ly), 5, (0,0,255), -1)
            cv2.circle(draw,(rx,ry), 5, (0,255,255), -1)
            cv2.circle(draw,(w/2,h/2), 5, (255,0,255), -1)


            cv2.imshow('map',draw)
            print "Press any key(on image) to continue"
            cv2.waitKey(0)
        else:
            print code
