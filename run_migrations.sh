#!/bin/bash

# Script para ejecutar migraciones de base de datos

set -e

echo "🔄 Ejecutando migraciones..."

# Configuración de base de datos desde .env o valores por defecto
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-tracker_user}
DB_NAME=${DB_NAME:-tracker_db}

export PGPASSWORD=${DB_PASSWORD:-tracker_pass}

# Ejecutar migración
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f migrations/001_initial_schema.sql

echo "✅ Migraciones ejecutadas correctamente"
