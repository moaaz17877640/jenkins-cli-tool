# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.12-alpine AS builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . /app/
RUN pip install --no-cache-dir .

# ==========================================
# Stage 2: Runner 
# ==========================================
FROM python:3.12-alpine


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

# Create a non-root user for security
RUN adduser -D cliuser
USER cliuser

ENTRYPOINT ["jenkins-cli"]
CMD ["--help"]
