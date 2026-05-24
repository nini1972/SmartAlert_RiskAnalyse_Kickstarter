# Multi-stage Dockerfile for SmartAlert Risk Analysis Kickstarter

# ---------- Stage 1: Build Frontend ----------
FROM node:20-alpine AS frontend-builder

# Set working directory
WORKDIR /app

# Install frontend dependencies
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile

# Copy frontend source
COPY frontend/ .

# Build frontend for production
ARG FRONTEND_ENV
ENV FRONTEND_ENV=${FRONTEND_ENV}
RUN echo "${FRONTEND_ENV}" | tr ',' '\n' > .env
RUN yarn build

# ---------- Stage 2: Install Python Dependencies ----------
FROM python:3.11-slim AS python-deps

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ---------- Stage 3: Production Backend ----------
FROM python:3.11-slim AS backend-production

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from previous stage
COPY --from=python-deps /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy backend source
COPY backend/ .

# Create necessary directories
RUN mkdir -p logs

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# ---------- Stage 4: Final Production Image ----------
FROM nginx:stable-alpine AS production

# Install nginx extras and utilities
RUN apk add --no-cache \
    bash \
    python3 \
    py3-pip

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/build /usr/share/nginx/html

# Copy backend from production stage
COPY --from=backend-production /app /backend

# Copy configuration files
COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh

# Install Python dependencies for backend
RUN pip3 install --break-system-packages -r /backend/requirements.txt

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Create non-root user
RUN addgroup -g 101 -S appgroup && adduser -S -G appgroup -u 101 appuser

# Change ownership of necessary directories
RUN chown -R appuser:appuser /var/cache/nginx \
    /var/run \
    /var/log/nginx \
    /backend

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start services
ENTRYPOINT ["/entrypoint.sh"]