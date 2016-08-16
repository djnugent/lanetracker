'''
parse args
--onboard : runs the autopilot, camera node, and CV node on the car
--client  : runs the autopilot, camera node on the car, and CV node offboard
--server  : runs CV node on a laptop
--sim     : simulates the entire echo system
'''

def sys_call(cmd,wait=False):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if wait:
        p.wait()
        out,error = p.communicate()
        return out.decode("utf-8"), error.decode("utf-8")


def onboard():
    #start ardurover
    sys_call(["APMRover.elf"])

    #start ROScore

    #start mavros

    #start camera node

    #start CV node

def client():
    #start ardurover
    sys_call("sudo ./APMrover2.elf -A udp:192.168.1.2:14550")

    #start ROScore

    #start camera node

def server():
    #start ROScore

    #start mavros

    #start CV node

def sim():
    #start ardurover sim
    sys_call("ardupilot/APMrover2/tools/autotest/sim_vehicle.sh")

    #start ROScore
    sys_call("roscore")

    #start mavros
    sys_call("ros/roslaunch mavros.launch")

    #start mavros_gazebo_bridge
    sys_call("python ros/sim.py")

    #start gazebo

    #start CV node
