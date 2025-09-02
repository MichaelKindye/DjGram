FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY . .

RUN chown -R appuser:appgroup /app

USER appuser

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=DjMessage.DJANGO_SETTINGS_MODULE

CMD ["daphne", "-b", "0.0.0.0", "-p", "10000", "DjMessage.asgi:application"]