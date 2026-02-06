#!/bin/bash

# Configuración de colores para la terminal
GREEN='\033[0-32m'
BLUE='\033[0-34m'
NC='\033[0m' # No Color

echo -e "${BLUE}--- 🚀 Iniciando Despliegue SGL ---${NC}"

# 1. Bajar cambios de Git
echo -e "${BLUE}📥 Sincronizando con el repositorio (git pull)...${NC}"
git pull
if [ $? -ne 0 ]; then
    echo "❌ Error en git pull. Despliegue cancelado."
    exit 1
fi

# 2. Activar entorno virtual
echo -e "${BLUE}🐍 Activando entorno virtual...${NC}"
source .env/bin/activate

# 3. Recolectar estáticos
echo -e "${BLUE}📦 Recolectando archivos estáticos...${NC}"
python manage.py collectstatic --link --no-default-ignore --noinput

# 4. Reiniciar Servicios
echo -e "${BLUE}🔄 Reiniciando Supervisor (sgrh)...${NC}"
sudo supervisorctl restart sgrh

echo -e "${BLUE}🌐 Reiniciando Nginx...${NC}"
sudo service nginx restart

echo -e "${GREEN}✅ ¡Despliegue finalizado con éxito!${NC}"