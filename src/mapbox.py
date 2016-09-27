from urllib2 import URLError
from urllib2 import urlopen
import cv2
import numpy as np
import os

'''
mapbox.py - This library is a python wrapper for the mapbox static API

parameters -    access token : Be sure you have set your MAPBOX_ACCESS_TOKEN environment variable or provide to the constrcutor
                username : owner of the tileset, usually mapbox for stock tilesets or your username for user made tilesets
                style id : tileset id from the specified user

'''

class Mapbox():

    def __init__(self, username = 'mapbox', style_id = 'streets-v8', access_token = None):
        #get access_token from enviroment or program
        self.access_token =  access_token or os.environ.get('MapboxAccessToken') or os.environ.get('MAPBOX_ACCESS_TOKEN')

        if self.access_token is None:
            print "WARNING: Be sure you have set your MAPBOX_ACCESS_TOKEN environment variable or pass access_token into constrcutor"

        self.username = username
        self.style_id = style_id

    def static_image(self,lat,lon,zoom,bearing=0,pitch=0,width=400,height=400,retina=False):
        uri = 'https://api.mapbox.com/styles/v1/'   #base_uri
        uri += self.username + "/"                  #username
        uri += self.style_id + "/static/"           #style_id
        uri += str(lon) + ','                            #lon(-180 to 180)
        uri += str(lat) + ','                            #lat(-90 to 90)
        uri += str(zoom) + ','                           #zoom(decimal 0 to 22)
        uri += str(bearing) + ','                        #bearing(0 to 360)
        uri += str(pitch) + '/'                          #pitch(0 to 60)
        uri += str(width) + 'x' + str(height)                 #width/height(1 to 1280)
        if retina:                                  #retina image
            uri += '@2x'
        uri += '?access_token=' + self.access_token

        try:
            resp = urlopen(uri)
    	    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    	    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            return 200, image
        except URLError as e:
            return e.code(), None


if __name__ == '__main__':
    lat, lon = 39.539207, -122.330665
    mapbox = Mapbox(username = 'djnugent', style_id = 'cirwqwpwc001sgwkoo9nok0l2')
    code, im = mapbox.static_image(lat,lon,18,pitch=30)

    if code == 200:
        cv2.imshow('map',im)
        cv2.waitKey(0)
    else:
        print code
