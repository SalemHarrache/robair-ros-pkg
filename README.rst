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

    make robot


Displays information about ROS topics with rostopic command-line  

::

    rostopic echo /info/battery
