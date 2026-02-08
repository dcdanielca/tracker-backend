#!/bin/bash

# Script para verificar permisos y configuración de Docker
# Uso: ./scripts/check-docker.sh

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🔍 Verificando configuración de Docker...${NC}\n"

# 1. Verificar que Docker esté instalado
echo -n "1. Verificando que Docker esté instalado... "
if command -v docker >/dev/null 2>&1; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    echo -e "${GREEN}✓ Docker $DOCKER_VERSION${NC}"
else
    echo -e "${RED}✗ Docker no está instalado${NC}"
    echo -e "${YELLOW}Instala Docker desde: https://docs.docker.com/engine/install/${NC}"
    exit 1
fi

# 2. Verificar que Docker Compose esté instalado
echo -n "2. Verificando que Docker Compose esté instalado... "
if docker compose version >/dev/null 2>&1; then
    COMPOSE_VERSION=$(docker compose version --short)
    echo -e "${GREEN}✓ Docker Compose $COMPOSE_VERSION${NC}"
else
    echo -e "${RED}✗ Docker Compose no está instalado${NC}"
    exit 1
fi

# 3. Verificar que el servicio de Docker esté corriendo
echo -n "3. Verificando que Docker esté corriendo... "
if systemctl is-active --quiet docker 2>/dev/null || pgrep -x dockerd >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker está activo${NC}"
else
    echo -e "${RED}✗ Docker no está corriendo${NC}"
    echo -e "${YELLOW}Inicia Docker con: sudo systemctl start docker${NC}"
    exit 1
fi

# 4. Verificar permisos para ejecutar Docker
echo -n "4. Verificando permisos de Docker... "
if docker ps >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Tienes permisos para ejecutar Docker${NC}"
elif groups | grep -q docker; then
    echo -e "${YELLOW}⚠ Estás en el grupo docker pero necesitas reiniciar sesión${NC}"
    echo -e "${YELLOW}Soluciones:${NC}"
    echo -e "  1. Ejecuta: ${GREEN}newgrp docker${NC} (para esta sesión)"
    echo -e "  2. Cierra sesión y vuelve a iniciar (permanente)"
    echo ""
    echo -e "${YELLOW}¿Deseas que intente ejecutar con newgrp? (requiere que vuelvas a ejecutar el comando)${NC}"
    exit 2
else
    echo -e "${RED}✗ No tienes permisos para ejecutar Docker${NC}"
    echo -e "${YELLOW}Solución: Agrégarte al grupo docker${NC}"
    echo -e "  ${GREEN}sudo usermod -aG docker $USER${NC}"
    echo -e "  Luego cierra sesión y vuelve a iniciar"
    exit 1
fi

# 5. Verificar que el archivo .env exista
echo -n "5. Verificando archivo .env... "
if [ -f .env ]; then
    echo -e "${GREEN}✓ .env existe${NC}"
else
    echo -e "${YELLOW}⚠ .env no existe${NC}"
    echo -e "${YELLOW}Creando .env desde .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env creado${NC}"
    else
        echo -e "${RED}✗ .env.example no encontrado${NC}"
        exit 1
    fi
fi

# 6. Verificar configuración en .env
echo -n "6. Verificando configuración de base de datos en .env... "
if grep -q "DB_HOST=" .env && grep -q "DB_USER=" .env && grep -q "DB_PASSWORD=" .env; then
    echo -e "${GREEN}✓ Variables de entorno configuradas${NC}"
else
    echo -e "${YELLOW}⚠ Faltan algunas variables de entorno${NC}"
fi

# 7. Verificar puertos disponibles
echo -n "7. Verificando puertos disponibles... "
PORTS_IN_USE=()

# Puerto 5432 (PostgreSQL)
if ss -tuln 2>/dev/null | grep -q ":5432 " || netstat -tuln 2>/dev/null | grep -q ":5432 "; then
    PORTS_IN_USE+=("5432 (PostgreSQL)")
fi

# Puerto 8000 (FastAPI)
if ss -tuln 2>/dev/null | grep -q ":8000 " || netstat -tuln 2>/dev/null | grep -q ":8000 "; then
    PORTS_IN_USE+=("8000 (FastAPI)")
fi

if [ ${#PORTS_IN_USE[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ Puertos disponibles${NC}"
else
    echo -e "${YELLOW}⚠ Puertos en uso: ${PORTS_IN_USE[*]}${NC}"
    echo -e "${YELLOW}Detén los servicios que usan estos puertos o cámbialos en .env${NC}"
fi

# 8. Verificar espacio en disco
echo -n "8. Verificando espacio en disco... "
AVAILABLE_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -gt 5 ]; then
    echo -e "${GREEN}✓ Espacio disponible: ${AVAILABLE_SPACE}GB${NC}"
else
    echo -e "${YELLOW}⚠ Espacio limitado: ${AVAILABLE_SPACE}GB${NC}"
fi

echo ""
echo -e "${GREEN}✅ Verificación completada!${NC}"
echo ""
echo -e "${YELLOW}Comandos útiles:${NC}"
echo -e "  ${GREEN}make docker-up${NC}       - Levantar servicios"
echo -e "  ${GREEN}make db-up${NC}           - Solo base de datos"
echo -e "  ${GREEN}make docker-logs${NC}     - Ver logs"
echo -e "  ${GREEN}make help${NC}            - Ver todos los comandos"
