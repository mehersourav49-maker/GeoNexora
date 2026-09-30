
# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-build

WORKDIR /frontend

COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Prepare the FastAPI application
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install backend dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code
COPY backend/ ./backend/

# Copy the built frontend into the backend directory
COPY --from=frontend-build /frontend/dist ./backend/static/

WORKDIR /app/backend

# Render provides PORT at runtime
EXPOSE 10000

CMD ["sh", "-c", "if [ \"${SEED_DEMO_DATA:-false}\" = \"true\" ]; then python seed_demo_data_safe.py || exit 1; fi; exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
