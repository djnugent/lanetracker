#!/usr/bin/env python
import rospy
import IPython
from geometry_msgs.msg import PoseStamped, TwistStamped, Twist, Vector3
from gazebo_msgs.msg import ModelState, ModelStates



class MAVGazBridge():

    def __init__(self, model_name):
        self.model_name = "cart_front_steer"
        self.pose = None
        self.vel = None

    def run(self):
        rospy.init_node('mavros_gazebo_bridge', anonymous=True)

        rospy.Subscriber("/mavros/local_position/velocity", TwistStamped , self.vel_callback)
        rospy.Subscriber("/mavros/local_position/pose", PoseStamped , self.pose_callback)
        #rospy.Subscriber("/gazebo/model_states",ModelStates,gaz_callback)

        self.pub = rospy.Publisher('/gazebo/set_model_state', ModelState, queue_size=10)

        rospy.spin()




    def pose_callback(self,mav_pose):
        #rospy.loginfo(mav_pose)
        #IPython.embed()
        self.pose = mav_pose.pose
        if self.vel is not None:
            self.publish()


    def vel_callback(self,mav_vel):
        #rospy.loginfo(mav_vel)
        self.vel = mav_vel.twist
        if self.pose is not None:
            self.publish()

    def gaz_callback(self,gaz):
        rospy.loginfo(gaz)
        IPython.embed()

    def publish(self):
        gaz = ModelState()
        gaz.model_name = self.model_name
        gaz.pose = self.pose
        gaz.twist = self.vel

        self.pub.publish(gaz)
        rospy.loginfo(gaz)
        self.pose, self.vel = None, None


if __name__ == '__main__':
    bridge = MAVGazBridge("cart_front_steer")
    bridge.run()
