FROM python:3.10 AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-public.txt .
COPY requirements-private.txt .

RUN pip install --upgrade pip && \ 
     pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements-public.txt && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements-private.txt



FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y systemd --no-install-recommends  && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \ 
    pip install --upgrade pip --no-cache-dir

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements-public.txt .
COPY --from=builder /app/requirements-private.txt .

RUN pip install --no-cache /wheels/* && \
    rm -rf /wheels

COPY app.py .
COPY wsgi.py .

RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

USER app

EXPOSE 5000

CMD [ "python3", "-m" , "gunicorn", "--bind=0.0.0.0:5000", "wsgi:app"]