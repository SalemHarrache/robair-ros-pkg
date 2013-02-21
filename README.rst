Robair ROS stack
################


Get sources
===========


::

   roscd
   git clone git@github.com:SalemHarrache/robair-ros-pkg.git


Run Test Node
=============


::

    roscd robair-ros-pkg
    rosmake


::

    roslaunch robair_test_node usb_cam-test.launch


Open a new terminal and execute:

::

    rosrun rqt_graph rqt_graph

