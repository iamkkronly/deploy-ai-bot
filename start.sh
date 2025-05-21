#!/bin/bash
gunicorn bot:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT


chmod +x start.sh