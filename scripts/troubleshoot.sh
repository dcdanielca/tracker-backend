#!/bin/bash

# Script para diagnosticar problemas comunes
# Uso: ./scripts/troubleshoot.sh

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   🔍 Tracker Backend - Diagnóstico    ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}\n"

# Función para mostrar sección
section() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# 1. Estado de Docker
section "1. Estado de Docker"
echo "Docker version:"
docker --version 2>&1 || echo -e "${RED}Docker no encontrado${NC}"
echo ""
echo "Docker Compose version:"
docker compose version 2>&1 || echo -e "${RED}Docker Compose no encontrado${NC}"
echo ""
echo "Docker daemon status:"
systemctl is-active docker 2>&1 || echo -e "${RED}Docker no está corriendo${NC}"

# 2. Permisos
section "2. Permisos de Usuario"
echo "Usuario actual: $USER"
echo "Grupos: $(groups)"
echo ""
if groups | grep -q docker; then
    echo -e "${GREEN}✓ Usuario en grupo docker${NC}"
else
    echo -e "${RED}✗ Usuario NO está en grupo docker${NC}"
fi
echo ""
echo "Prueba de permisos Docker:"
if docker ps >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Puede ejecutar comandos Docker${NC}"
else
    echo -e "${RED}✗ No puede ejecutar comandos Docker${NC}"
    echo -e "${YELLOW}Solución: newgrp docker o reiniciar sesión${NC}"
fi

# 3. Puertos
section "3. Puertos"
echo "Verificando puertos críticos:"
for port in 5432 8000 5050; do
    echo -n "Puerto $port: "
    if ss -tuln 2>/dev/null | grep -q ":$port " || netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo -e "${YELLOW}EN USO${NC}"
        echo "  Proceso:"
        sudo lsof -i :$port 2>/dev/null || ss -tlnp 2>/dev/null | grep ":$port" || echo "  (no se pudo determinar)"
    else
        echo -e "${GREEN}DISPONIBLE${NC}"
    fi
done

# 4. Estado de contenedores
section "4. Contenedores Docker"
echo "Contenedores relacionados con tracker:"
if docker ps -a 2>/dev/null | grep tracker; then
    echo ""
else
    echo -e "${YELLOW}No hay contenedores de tracker${NC}"
fi
echo ""
echo "Todos los contenedores:"
docker ps -a 2>/dev/null || echo -e "${RED}No se pueden listar contenedores${NC}"

# 5. Docker Compose
section "5. Estado de Docker Compose"
if [ -f docker-compose.yml ]; then
    echo -e "${GREEN}✓ docker-compose.yml encontrado${NC}"
    echo ""
    echo "Servicios definidos:"
    docker compose config --services 2>&1 || echo -e "${RED}Error al leer docker-compose.yml${NC}"
    echo ""
    echo "Estado de servicios:"
    docker compose ps 2>&1 || echo -e "${RED}No se puede obtener estado${NC}"
else
    echo -e "${RED}✗ docker-compose.yml no encontrado${NC}"
fi

# 6. Variables de entorno
section "6. Variables de Entorno"
if [ -f .env ]; then
    echo -e "${GREEN}✓ .env encontrado${NC}"
    echo ""
    echo "Variables configuradas (valores ocultos):"
    grep -E "^[A-Z_]+=" .env | cut -d'=' -f1 | sed 's/^/  /'
else
    echo -e "${RED}✗ .env no encontrado${NC}"
    echo -e "${YELLOW}Crea uno: cp .env.example .env${NC}"
fi

# 7. Logs recientes
section "7. Logs Recientes"
if docker compose ps 2>/dev/null | grep -q "tracker"; then
    echo "Últimas 20 líneas de logs:"
    docker compose logs --tail=20 2>&1 || echo -e "${RED}No se pueden obtener logs${NC}"
else
    echo -e "${YELLOW}No hay servicios corriendo${NC}"
fi

# 8. Conectividad de red
section "8. Conectividad"
echo "Probando conectividad local:"
echo -n "  localhost:8000 (API): "
if curl -s -m 2 http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Accesible${NC}"
else
    echo -e "${RED}✗ No accesible${NC}"
fi

echo -n "  localhost:5432 (PostgreSQL): "
if timeout 2 bash -c "cat < /dev/null > /dev/tcp/localhost/5432" 2>/dev/null; then
    echo -e "${GREEN}✓ Accesible${NC}"
else
    echo -e "${RED}✗ No accesible${NC}"
fi

# 9. Espacio en disco
section "9. Recursos"
echo "Espacio en disco:"
df -h . | tail -1
echo ""
echo "Uso de Docker:"
docker system df 2>/dev/null || echo -e "${RED}No se puede obtener uso de Docker${NC}"

# 10. Recomendaciones
section "10. Recomendaciones"

ISSUES=()

if ! docker ps >/dev/null 2>&1; then
    ISSUES+=("${RED}✗${NC} No tienes permisos de Docker - ejecuta: newgrp docker")
fi

if ! [ -f .env ]; then
    ISSUES+=("${RED}✗${NC} Falta archivo .env - ejecuta: cp .env.example .env")
fi

if ! docker compose ps 2>/dev/null | grep -q "tracker-db.*running"; then
    ISSUES+=("${YELLOW}⚠${NC} Base de datos no está corriendo - ejecuta: make db-up")
fi

if ss -tuln 2>/dev/null | grep -q ":8000 " || netstat -tuln 2>/dev/null | grep -q ":8000 "; then
    ISSUES+=("${YELLOW}⚠${NC} Puerto 8000 en uso - detén el servicio o cambia el puerto en .env")
fi

if [ ${#ISSUES[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ No se detectaron problemas obvios${NC}"
else
    echo -e "${YELLOW}Problemas detectados:${NC}"
    for issue in "${ISSUES[@]}"; do
        echo -e "  $issue"
    done
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Comandos útiles para solucionar problemas:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  ${GREEN}./scripts/check-docker.sh${NC}  - Verificar configuración"
echo -e "  ${GREEN}./scripts/init-project.sh${NC}  - Inicializar proyecto"
echo -e "  ${GREEN}make docker-logs${NC}          - Ver logs completos"
echo -e "  ${GREEN}make docker-clean${NC}         - Limpiar y empezar de nuevo"
echo -e "  ${GREEN}make help${NC}                 - Ver todos los comandos"
echo ""
