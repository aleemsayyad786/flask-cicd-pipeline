# ─────────────────────────────────────────────
# Stage 1 — Builder
# Install deps in an isolated layer so the
# final image doesn't carry pip/build tools.
# ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install only what's needed to compile wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ─────────────────────────────────────────────
# Stage 2 — Runtime
# Slim final image: no build tools, no pip cache
# ─────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Security: run as non-root user
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app

# Copy pre-built wheels from builder and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

# Copy application source
COPY app/ ./app/

# Drop to non-root
USER appuser

# Metadata labels (OCI standard)
ARG APP_VERSION=1.0.0
ARG BUILD_DATE
ARG GIT_SHA
LABEL org.opencontainers.image.title="flask-cicd-demo"
LABEL org.opencontainers.image.version="${APP_VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${GIT_SHA}"
LABEL org.opencontainers.image.source="https://github.com/YOUR_USERNAME/flask-cicd-pipeline"

ENV APP_VERSION=${APP_VERSION}
ENV FLASK_ENV=production
ENV PORT=5000

EXPOSE 5000

# Gunicorn: production-grade WSGI server
# workers = 2*CPU + 1  (good baseline for I/O apps)
CMD ["gunicorn", "app.main:app", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
