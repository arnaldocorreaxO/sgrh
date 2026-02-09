#!/bin/bash

NAME="sgrh"
# /home/tic/sgrh/app/deploy
DIRECTORY=$(cd `dirname $0` && pwd)
# /home/tic/sgrh/app (Sube un nivel)
APPDIR=`dirname $DIRECTORY`
# /home/tic/sgrh (Sube a la raíz)
DJANGODIR=`dirname $APPDIR`

# Ruta del entorno virtual según lo que me indicaste
VENV_PATH="${DJANGODIR}/.env/bin/activate"

SOCKFILE=/tmp/gunicorn.sock
LOGDIR=${DJANGODIR}/logs/gunicorn.log
USER=tic
GROUP=tic
NUM_WORKERS=5
DJANGO_SETTINGS_MODULE=config.production
DJANGO_WSGI_MODULE=config.wsgi

# Limpiar socket previo
rm -frv $SOCKFILE

echo "Iniciando $NAME"
echo "Directorio del Script: $DIRECTORY"
echo "Raíz del Proyecto: $DJANGODIR"

# Navegar a la raíz para ejecutar gunicorn
cd $DJANGODIR

# Activar el entorno virtual
if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
else
    echo "ERROR: Entorno virtual no encontrado en $VENV_PATH"
    exit 1
fi

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Crear el directorio para los logs si no existe
mkdir -p ${DJANGODIR}/logs

# Ejecutar Gunicorn
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=$LOGDIR