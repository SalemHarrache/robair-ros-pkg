#!/bin/bash
#
# Script d'instalation des dependances pour le projet
#
# Authors : Salem Harrache
#


if [ $EUID -ne 0 ]; then
  echo "Error : Must run as root" 1>&2
  exit 1
fi

OS=$(lsb_release -si)
DATE=`date +"%Y%m%d%H%M%S"`
LOG_FILE="/tmp/robair-setup-python-$DATE.log"

if [ $OS != "Ubuntu" ]; then
    echo Error: incompatible system
    exit 1
fi

# Functions
#-----------------------------------------------------------------------------

displaymessage() {
  echo "$*"
}

displaytitle() {
  displaymessage "--------------------------------------------------------------------------------"
  displaymessage "$*"
  displaymessage "--------------------------------------------------------------------------------"
}

displayerror() {
  displaymessage "$*" >&2
}

# First parameter: ERROR CODE
# Second parameter: MESSAGE
displayerrorandexit() {
  local exitcode=$1
  shift
  displayerror "$*"
  exit $exitcode
}

# First parameter: MESSAGE
# Others parameters: COMMAND (! not |)
displayandexec() {
  local message=$1
  echo -n "[En cours] $message"
  shift
  echo ">>> $*" >> $LOG_FILE 2>&1
  sh -c "$*" >> $LOG_FILE 2>&1
  local ret=$?
  if [ $ret -ne 0 ]; then
    echo -e "\r\e[0;31m   [ERROR]\e[0m $message"
  else
    echo -e "\r\e[0;32m      [OK]\e[0m $message"
  fi
  return $ret
}

# Start install
#-----------------------------------------------------------------------------

displaytitle "Install prerequisites"

# update system deposit
displayandexec "Update the repositories list" apt-get update


displaytitle "Python tools"

displayandexec "Install Python development tools" apt-get -y install python2.7 ipython
displayandexec "Install Python-dev" apt-get -y install python2.7-dev python-pip
displayandexec "Install Python packages manager (pip)" apt-get -y install python-pip
displayandexec "Install GIT" apt-get -y install git
displayandexec "Install development tools" apt-get -y install python2.7-dev python-pip git
displayandexec "Update distribute" pip install -U distribute
displayandexec "Install virtualenv" pip install -U virtualenv
displayandexec "Install pep8 & pyflakes" pip install -U pep8 pyflakes
displayandexec "Install flask (http framework)" pip install -U pep8 flask
displayandexec "Install sleekxmpp" pip install -U sleekxmpp
displayandexec "Install dnspython" pip install -U dnspython
displayandexec "Install nxt-python" pip install -U nxt-python

displaytitle "Redis"
displayandexec "Install redis-server" sudo apt-get install redis-server
displayandexec "Install redis-client" pip install -U redis

displaytitle "GStreamer installation"
displayandexec "Install gstreamer-tools" apt-get -y install gstreamer-tools

displaytitle "PySide PPA installation"

if [ "$(dpkg-query -W -f='${Status}' python-pyside)" == "install ok installed" ]
then
displayandexec "Already instaled" echo > /dev/null
else
echo "deb http://ppa.launchpad.net/pyside/ppa/ubuntu precise main" >> /etc/apt/sources.list.d/pyside.list
displayandexec "Add PPA repository" apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 073700C1
displayandexec "Update the repositories list" apt-get update
displayandexec "Install PySide from PPA" apt-get -y install python-pyside
fi
displaytitle "Finish"
displayandexec "Clean" "apt-get autoclean -y && apt-get -y clean && apt-get -y autoremove"

echo ""
echo "Installation finished"
echo "Installation script  log file:    $LOG_FILE"
