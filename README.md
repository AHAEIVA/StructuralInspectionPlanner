StructuralInspectionPlanner
===========================

**Remote System**

This toolbox is designed to run on a remote system.

Installing the toolbox
---------------------------
To use the toolbox a ROS indigo installation with catkin set-up and the following extra packages are required:

```
libeigen3-dev
ros-indigo-tf
ros-indigo-rviz
ros-indigo-octomap
ros-indigo-octomap-msgs
```

Once these are there, a baseline example on how to get and install the tool is the following:

```sh
$ mkdir catkin_ws_repos # assuming you want to enter a new catkin directory
$ cd catkin_ws_repos # alternatively just cd your normal catkin workspace
$ mkdir src # assuming this folder does not exist
$ cd src/
$ catkin_init_workspace
$ git clone https://github.com/AHAEIVA/StructuralInspectionPlanner.git
$ cd ..
$ catkin_make
$ source devel/setup.bash
```

Running the pipe example
---------------------------
To run the pipe example, execute the following commands in separate terminals:

Shell #1
```sh
rosrun request bigBen
```

Shell #2
```sh
roslaunch koptplanner bigBen.launch
```

Shell #3
```sh
rviz -d rviz_sip.rviz
