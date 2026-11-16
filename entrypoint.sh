#!/bin/sh
set -e

# Executa as migrações do banco de dados
alembic upgrade head

# Inicia a aplicação (exec para receber os sinais de parada do Docker)
exec fastapi run fast_zero/app.py --host 0.0.0.0 --port 8000
