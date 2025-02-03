#!/bin/bash
# SPDX-License-Identifier: Apache-2.0

cd /app/server

# Wait for 5 seconds to allow services to initialize
sleep 5
echo "Starting server..."

# Run database migrations
echo "Running database migrations..."
echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Database URL: $DATABASE_URL"
PYTHONPATH=/app/server uv run alembic upgrade head || {
    echo "Migration failed with status $?"
    echo "Checking database connection..."
    uv run python -c "
import asyncio
import asyncpg
async def test_db():
    try:
        conn = await asyncpg.connect('$DATABASE_URL')
        await conn.close()
        print('Database connection successful')
    except Exception as e:
        print(f'Database connection failed: {e}')
asyncio.run(test_db())
"
}

# Start the FastAPI server with uvicorn using the virtual environment's Python
echo "Running uvicorn with uv..."
uv run python -m uvicorn server.main:app --host 0.0.0.0 --port 32100 --reload --reload-dir /app/server/server
