# Build stage
FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# Copy requirements file
COPY modules/aidriver_datamodel/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
COPY modules/aidriver_datamodel /app
RUN pip install --no-cache-dir -e .

# Set Python path to include the modules
ENV PYTHONPATH=/app:/app/modules:$PYTHONPATH

# Create a non-root user
RUN useradd -m appuser
USER appuser

# Expose the port the app runs on
EXPOSE 18000

# Set the entrypoint
ENTRYPOINT ["uvicorn"]

# Set default command
CMD ["aidriver_datamodel.api.app:app", "--host", "0.0.0.0", "--port", "18000"]