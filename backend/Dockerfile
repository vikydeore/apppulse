#Stage 1: Build Dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system build essentials if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies locally
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime image
FROM python:3.11-slim

WORKDIR /app

#Copy python site-packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY . /app

#Security best practice: Create and switch to a non-root user
RUN useradd -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
