include $(shell rospack find mk)/cmake_stack.mk

SHELL := /bin/bash

# these files should pass pyflakes
# exclude ./env/, which may contain virtualenv packages
PYFLAKES_WHITELIST=$(shell find . -name "*.py" ! -path "./doc/*" \
                    ! -path "./.tox/*" ! -path "./env/*" \
                    ! -path "*/compat.py" )

test:
	tox

pyflakes:
	pyflakes ${PYFLAKES_WHITELIST}

pep:
	pep8 --first .

gitclean:
	git clean -Xfd

doc:
	rosrun rosdoc rosdoc $(ls -a | grep robair)
