FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY main.py .

RUN useradd --create-home --shell /usr/sbin/nologin appuser
USER appuser

CMD ["python", "main.py"]
