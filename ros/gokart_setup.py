


def client():
    #install ardupilot
    sys_call("rm APMrover2.elf")
    sys_call("wget http://firmware.ardupilot.org/Rover/stable/" + board + "/APMrover2.elf")
    sys_call("sudo chmod +x APMrover2.elf")

    #install ros
    #TODO verify os name
    sys_call('sudo update-locale LANG=C LANGUAGE=C LC_ALL=C LC_MESSAGES=POSIX')
    sys_call('sudo echo "deb http://packages.ros.org/ros/ubuntu trusty main" > /etc/apt/sources.list.d/ros-latest.list')
    sys_call('sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 0xB01FA116')
    sys_call('sudo apt-get update')
    sys_call('sudo apt-get install ros-jade-ros-base ros-jade-usb-cam ros-jade-mavlink ros-jade-mavros ros-jade-cv-bridge ros-jade-image-proc')
    sys_call('sudo apt-get install python-rosdep')
    sys_call('sudo rosdep init')
    sys_call('rosdep update')
    sys_call('echo "source /opt/ros/jade/setup.bash" >> ~/.bashrc')
    sys_call('sudo apt-get install python-rosinstall')
