import math
import time
from dronekit import connect, VehicleMode
from mission import read_mission, mission_to_locations
from position_vector import PositionVector


#connect to sitl
vehicle = connect("127.0.0.1:14551", wait_ready=True,rate=50)

#change to manual mode
print "\nSet Vehicle.mode = MANUAL (currently: %s)" % vehicle.mode.name
vehicle.mode = VehicleMode("MANUAL")
while not vehicle.mode.name=='MANUAL':  #Wait until mode has changed
    print " Waiting for mode change ..."
    time.sleep(1)

#check that vehicle is armable
while not vehicle.is_armable:
    print " Waiting for vehicle to initialise..."
    time.sleep(1)

#arm vehicle
print "\nSet Vehicle.armed=True (currently: %s)" % vehicle.armed
vehicle.armed = True
while not vehicle.armed:
    print " Waiting for arming..."
    time.sleep(1)
print " Vehicle is armed: %s" % vehicle.armed


#get Vehicle Home location
while not vehicle.home_location:
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    if not vehicle.home_location:
        print " Waiting for home location ..."

#Set origin point to home
PositionVector.set_home_location(vehicle.home_location)

#Read waypoints from mission file
waypoints = mission_to_locations(read_mission("thunderhill.mission"))

#navigate waypoints in manual mode
DIST_THRESH = 4 #distance to waypoint before moving onto next waypoint
P_TURN = 1  #p term of navigation controller
SPEED = 100 #throttle level

wp_cnt = 1
for wp in waypoints:
    #convert global lat/lon local meters(position vectors)
    wp_posvec = PositionVector.get_from_location(wp)
    veh_posvec = PositionVector.get_from_location(vehicle.location.global_relative_frame)
    dist = PositionVector.get_distance_xy(veh_posvec,wp_posvec)


    while dist > DIST_THRESH:
        #calculate target_heading and heading error
        target_heading = math.degrees(PositionVector.get_bearing(veh_posvec,wp_posvec))
        error = target_heading - vehicle.heading
        #remap error from 0 to 360 -> -180 to 180
        if error > 180:
            error = error - 360
        if error < -180:
            error = 360 + error

        print "going to wp {}: {} meters, {} error".format(wp_cnt,dist,error)

        #calculate RC overrides(P controller)
        steering = max(min(int(P_TURN * error * min(1,dist/12.0) + 1500),1550),1450)
        throttle = int(500 * (SPEED/100.0) + 1500)

        #send RC overrides
        vehicle.channels.overrides['1'] = steering
        vehicle.channels.overrides['3'] = throttle

        #update at 50hz
        time.sleep(.02)

        #update vehicle position
        veh_posvec = PositionVector.get_from_location(vehicle.location.global_relative_frame)
        dist = PositionVector.get_distance_xy(veh_posvec,wp_posvec)

    print "next wp"
    wp_cnt +=1

#stop the vehicle at end of mission
vehicle.mode = VehicleMode("HOLD")
