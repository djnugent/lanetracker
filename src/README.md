# Lanetracker - src

This directory contains dronekit and openCV scripts. All files(except _recorder.py_) are designed to run on laptop but can be easily adapted to be run on a raspberrypi.

**cspline.py** - Script: Currently contains the math for calculating a cardinal spline.

**helpers.py** - Library: Contains computer vision helper functions

**lanedetect_edges.py** - Script: Detects lane using canny edge detection. Wish it worked better due to it's versatility in varying lighting conditions, but it gets confused by highly textured environments. Currently executes on a static file "test.mp4"

**lanedetect_threshold.py** - Script: Detects lane using HSV thresholding. Currently executes on a static file "test.mp4". Works better than **lanedetect_edges.py** but still susceptible to varying lighting conditions and highly dynamic scenes. Would like to replace with kmean segmentation. Currently executes on a static file "test.mp4"

**mapbox.py** - Library: Accesses static mapbox tiles. When run as a script it will load custom
thunderhill tiles. ***Be sure you set your MAPBOX_ACCESS_TOKEN environment variable or provide it when calling the library***

**mission.py** - Script: Reads a MAV mission file and detects lane centers from custom mapbox tiles. Currently executes on static file "thunderhill.mission"

**navigation.py** - Scripts: Reads a MAV mission file and drives the mission using RC_OVERRIDES. ***This is extremely dangerous and should only be used in SITL*** This requires SITL to be running. Currently executes on static file "thunderhill.mission"

**position_vector.py** - Library: Math library for working with GPS coordinates.

**recorder.py** - Script: To be run onboard a raspberrypi. It records test footage while the vehicle is armed.
