# Builder stage: install dependencies only
FROM python:3.11-slim AS builder
WORKDIR /build

# Layer: dependencies (change less often → better cache)
COPY app/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage: minimal image to run the app
FROM python:3.11-slim
WORKDIR /app

# Copy installed packages from builder (no build tools in runtime)
COPY --from=builder /root/.local /root/.local
COPY app/ .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8080
CMD ["python", "app.py"]
