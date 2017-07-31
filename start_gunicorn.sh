#!/bin/bash
NEME="enjoy_love" # Name of the application
DJANGODIR=/root/enjoylove/enjoylove # Django project directory
SOCKFILE=/root/enjoylove/run/gunicorn.sock # we will communicte using this unix socket
USER=root# the user to run as
GROUP=root
#GROUP=webapps # the group to run as
NUM_WORKERS=3 # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=enjoylove.settings # which settings file should Django use
DJANGO_WSGI_MODULE=enjoylove.wsgi # WSGI module name
PORT=8200

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
#source ../bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
gunicorn ${DJANGO_WSGI_MODULE}:application -b 0.0.0.0:$PORT --workers $NUM_WORKERS --user=$USER --group=$GROUP --bind=unix:$SOCKFILE --log-level=debug --log-file=-
