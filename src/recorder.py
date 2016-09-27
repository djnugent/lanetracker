import time
from dronekit import connect
import picamera
import os.path
import time



'''
recorder.py - 	Records footage from a raspberry pi camera onboard a Navio while the
				vehicle is armed. This script takes control of the camera and can
				NOT be run in parrallel with a CV script.

		usage - python recorder.py
				*Be sure that the "vids" directory exists in the home directory
'''



print "Waiting for boot: 30sec"
time.sleep(30)


vehicle = connect("127.0.0.1:14550", wait_ready=True)
camera  = picamera.PiCamera()
try:
	while True:

		print " Waiting for arming ..."
		while not vehicle.armed:  #Wait until armed
			time.sleep(0.5)

		#enumerate file name
		base_path = "/home/pi/vids/driving"
		i = 0
		while os.path.exists(base_path + str(i) + ".h264"):
			i += 1
		file_path = base_path + str(i) + ".h264"

		#start recording
		print "Armed: recording to {}".format(file_path)
		camera.start_recording(file_path)
		while vehicle.armed:
			time.sleep(1)

		print "Disarmed: Stopped recording"
		camera.stop_recording()

finally:
	camera.stop_recording()
	vehicle.close()
