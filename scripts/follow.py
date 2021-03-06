#!/usr/bin/env python
"""OpenCV feature detectors with ros CompressedImage Topics in python.

This example subscribes to a ros topic containing sensor_msgs 
CompressedImage. It converts the CompressedImage into a numpy.ndarray, 
then detects and marks features in that image. It finally displays 
and publishes the new image - again as CompressedImage topic.
"""
__author__ =  'Alex Fomenko & Simon Haller <simon.haller at uibk.ac.at>'
__version__=  '0.1'
__license__ = 'BSD'
# Python libs
import sys

# numpy and scipy
import numpy as np

# OpenCV
import cv2

# Ros libraries
import roslib
import rospy

# Ros Messages
from sensor_msgs.msg import CompressedImage
from geometry_msgs.msg import Twist
# We do not use cv_bridge it does not support CompressedImage in python
# from cv_bridge import CvBridge, CvBridgeError

# custom lib
from imgprocess.Line import Line

VERBOSE=False

class Line_finder:

    def __init__(self):
        '''Initialize ros publisher, ros subscriber'''
        rospy.init_node('line_finder', anonymous=False)
        # topic where we publish
        self.image_pub = rospy.Publisher("/detected_cte/image/compressed",
            CompressedImage, queue_size = 1)
        self.image_roi_pub = rospy.Publisher("/roi/image/compressed",
            CompressedImage, queue_size = 1)

        self.twist_pub = rospy.Publisher("/car_cmr/cmd_vel", Twist, queue_size = 1)
        # self.bridge = CvBridge()

        # subscribed Topic
        self.subscriber = rospy.Subscriber("/camera/image/compressed",
            CompressedImage, self.callback,  queue_size = 1)

        self.line = None

        if VERBOSE :
            print "subscribed to /camera/image/compressed"


    def callback(self, ros_data):
        '''Callback function of subscribed topic. 
        Here images get converted and features detected'''
        if VERBOSE :
            print 'received image of type: "%s"' % ros_data.format

        

        #### direct conversion to CV2 ####
        np_arr = np.fromstring(ros_data.data, np.uint8)
        # image_np = cv2.imdecode(np_arr, cv2.CV_LOAD_IMAGE_COLOR)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # OpenCV >= 3.0:
        
        if self.line == None:
            self.line = Line(img)

        time1 = rospy.Time.now()

        try:
            cte, outImg, roiImg = self.line.find_offset(img)
        except:
            cte = 0
            outImg = img
            roiImg = img

        
        time2 = rospy.Time.now()
        dur = time2 - time1
        # if VERBOSE :
        #     print '%s detector found: %s points in: %s sec.'%(method,
        #         len(featPoints),time2-time1)
        
        
        # Debug info
        rospy.loginfo("Cross track error: %s", cte)

        #### Create CompressedIamge ####
        msg = CompressedImage()
        msg.header.stamp = rospy.Time.now()
        msg.format = "jpeg"
        msg.data = np.array(cv2.imencode('.jpg', outImg)[1]).tostring()
        # Publish new image
        self.image_pub.publish(msg)

        #### Create CompressedIamge ####
        msg = CompressedImage()
        msg.header.stamp = rospy.Time.now()
        msg.format = "jpeg"
        msg.data = np.array(cv2.imencode('.jpg', roiImg)[1]).tostring()
        # Publish new image
        self.image_roi_pub.publish(msg)
        
        twist = Twist()
        twist.linear.x = 1.0
        twist.angular.z = -cte*0.015
        self.twist_pub.publish(twist)
        #self.subscriber.unregister()

    def shutdown(self):
        rospy.loginfo(rospy.get_caller_id() + " RCTeleop shutdown")


def main(args):
    '''Initializes and cleanup ros node'''
    lf = Line_finder()
    # rospy.init_node('line_finder', anonymous=False)
    try:
        rospy.spin()
    except KeyboardInterrupt:
    	# Stop the motors
        # twist = Twist()
        # twist.linear.x = 0
        # twist.angular.z = 0
        # self.twist_pub.publish(twist)
        print "Shutting down ROS Image feature detector module"

if __name__ == '__main__':
    main(sys.argv)