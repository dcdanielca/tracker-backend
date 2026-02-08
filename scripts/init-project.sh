#!/bin/bash

# Script de inicialización del proyecto
# Verifica todo y levanta los servicios
# Uso: ./scripts/init-project.sh

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   🎯 Tracker Backend - Inicialización ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}\n"

# 1. Verificar Docker
echo -e "${YELLOW}Paso 1: Verificando configuración de Docker...${NC}"
if ! ./scripts/check-docker.sh; then
    echo -e "${RED}❌ Error: La verificación de Docker falló${NC}"
    echo -e "${YELLOW}Por favor, soluciona los problemas indicados arriba${NC}"
    exit 1
fi

echo ""

# 2. Construir imágenes si no existen
echo -e "${YELLOW}Paso 2: Verificando imágenes de Docker...${NC}"
if ! docker images | grep -q "tracker-backend"; then
    echo -e "${YELLOW}📦 Construyendo imágenes de Docker...${NC}"
    docker compose build
    echo -e "${GREEN}✓ Imágenes construidas${NC}"
else
    echo -e "${GREEN}✓ Imágenes ya existen${NC}"
    echo -e "${YELLOW}¿Deseas reconstruir las imágenes? (y/N)${NC}"
    read -r -t 5 REBUILD || REBUILD="n"
    if [[ "$REBUILD" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}📦 Reconstruyendo imágenes...${NC}"
        docker compose build
    fi
fi

echo ""

# 3. Crear archivo .env si no existe
echo -e "${YELLOW}Paso 3: Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creando .env desde .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env creado${NC}"
    echo -e "${YELLOW}⚠  Revisa y ajusta las variables en .env si es necesario${NC}"
else
    echo -e "${GREEN}✓ .env ya existe${NC}"
fi

echo ""

# 4. Crear directorios necesarios
echo -e "${YELLOW}Paso 4: Creando directorios necesarios...${NC}"
mkdir -p backups logs
echo -e "${GREEN}✓ Directorios creados${NC}"

echo ""

# 5. Levantar servicios
echo -e "${YELLOW}Paso 5: Levantando servicios...${NC}"
echo -e "${YELLOW}¿Qué deseas levantar?${NC}"
echo "  1) Solo base de datos (desarrollo local)"
echo "  2) Todos los servicios (app + db)"
echo "  3) Todos + PgAdmin (completo)"
echo ""
read -r -t 10 -p "Selecciona una opción (1-3) [default: 2]: " OPTION || OPTION="2"

case $OPTION in
    1)
        echo -e "${YELLOW}🐳 Levantando solo base de datos...${NC}"
        docker compose up -d db
        ;;
    3)
        echo -e "${YELLOW}🐳 Levantando todos los servicios + PgAdmin...${NC}"
        docker compose --profile tools up -d
        ;;
    *)
        echo -e "${YELLOW}🐳 Levantando todos los servicios...${NC}"
        docker compose up -d
        ;;
esac

echo ""

# 6. Esperar a que la BD esté lista
echo -e "${YELLOW}Paso 6: Esperando que la base de datos esté lista...${NC}"
echo -n "Esperando"
for i in {1..30}; do
    if docker compose exec -T db pg_isready -U tracker_user -d tracker_db >/dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

if ! docker compose exec -T db pg_isready -U tracker_user -d tracker_db >/dev/null 2>&1; then
    echo -e " ${RED}✗${NC}"
    echo -e "${RED}❌ La base de datos no está lista${NC}"
    echo -e "${YELLOW}Revisa los logs: make docker-logs-db${NC}"
    exit 1
fi

echo ""

# 7. Verificar servicios
echo -e "${YELLOW}Paso 7: Verificando servicios...${NC}"
docker compose ps

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✅ Proyecto iniciado con éxito    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Mostrar URLs según lo que se levantó
echo -e "${BLUE}🌐 Servicios disponibles:${NC}"
if docker compose ps | grep -q "tracker-app.*running"; then
    echo -e "  ${GREEN}✓${NC} API:          http://localhost:8000"
    echo -e "  ${GREEN}✓${NC} Documentación: http://localhost:8000/docs"
    echo -e "  ${GREEN}✓${NC} Health Check: http://localhost:8000/health"
fi

if docker compose ps | grep -q "tracker-db.*running"; then
    echo -e "  ${GREEN}✓${NC} PostgreSQL:   localhost:5432"
fi

if docker compose ps | grep -q "tracker-pgadmin.*running"; then
    echo -e "  ${GREEN}✓${NC} PgAdmin:      http://localhost:5050"
    echo -e "      Email: admin@tracker.com"
    echo -e "      Pass:  admin"
fi

echo ""
echo -e "${BLUE}📋 Comandos útiles:${NC}"
echo -e "  ${GREEN}make docker-logs${NC}     - Ver logs de todos los servicios"
echo -e "  ${GREEN}make docker-logs-app${NC} - Ver logs de la aplicación"
echo -e "  ${GREEN}make docker-logs-db${NC}  - Ver logs de la base de datos"
echo -e "  ${GREEN}make docker-shell${NC}    - Acceder al shell del contenedor"
echo -e "  ${GREEN}make db-shell${NC}        - Acceder a PostgreSQL"
echo -e "  ${GREEN}make docker-down${NC}     - Detener servicios"
echo -e "  ${GREEN}make help${NC}            - Ver todos los comandos"
echo ""

# Probar la conexión si la app está corriendo
if docker compose ps | grep -q "tracker-app.*running"; then
    echo -e "${YELLOW}🧪 Probando la API...${NC}"
    sleep 2
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo -e "${GREEN}✓ API respondiendo correctamente${NC}"
    else
        echo -e "${YELLOW}⚠ La API aún no responde, espera unos segundos más${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 ¡Listo para desarrollar!${NC}"
