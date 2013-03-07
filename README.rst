Robair ROS stack
################


Get sources
===========

::

   roscd
   git clone git@github.com:SalemHarrache/robair-ros-pkg.git


Install dependencies
====================

::

    sudo ./setup-debs.sh



Run on Robot
============

::

    roscd robair-ros-pkg
    rosmake


::

    roslaunch robair_app robot.launch jid:=robot@server.com password:=secret


::

    rostopic echo /info/battery
