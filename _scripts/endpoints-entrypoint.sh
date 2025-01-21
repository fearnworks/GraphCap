# SPDX-License-Identifier: Apache-2.0
#!/bin/bash

# Start the FastAPI server with uvicorn
uvicorn GraphCap.server.app:app \
    --host "0.0.0.0" \
    --port 32100 \
    --reload \
    --reload-dir /app/GraphCap
