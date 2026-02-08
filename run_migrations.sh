#!/bin/bash

set -e

echo "🔄 Ejecutando migraciones..."

# Cargar variables desde .env de forma segura
if [ -f .env ]; then
  echo "📦 Cargando variables desde .env"
  set -a
  source .env
  set +a
else
  echo "⚠️ No se encontró .env, usando valores por defecto"
fi

# Configuración de base de datos
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-tracker_user}
DB_NAME=${DB_NAME:-tracker_db}

export PGPASSWORD=${DB_PASSWORD:-tracker_pass}

echo "➡️ Conectando a $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"

psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -f migrations/001_initial_schema.sql

echo "✅ Migraciones ejecutadas correctamente"