# syntax=docker/dockerfile:1

FROM python:3.13-slim

# Prevent .pyc files and force unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY main.py .

USER nobody:nogroup

EXPOSE 8080

ENTRYPOINT ["python", "main.py"]
