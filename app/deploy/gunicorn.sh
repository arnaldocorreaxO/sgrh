#!/bin/bash

NAME="sgrh"
DJANGODIR=/home/tic/sgrh
SOCKFILE=/home/tic/sgrh/run/gunicorn.sock
USER=tic
GROUP=tic
NUM_WORKERS=3
DJANGO_SETTINGS_MODULE=config.settings
DJANGO_WSGI_MODULE=config.wsgi

echo "Iniciando aplicación $NAME"

# Ir al directorio del proyecto
cd $DJANGODIR

# Activar el entorno virtual usando tu ruta específica
source /home/tic/sgrh/.env/bin/activate

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Crear el directorio para el socket si no existe
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Ejecutar Gunicorn
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=-