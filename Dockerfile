FROM python:3.13-slim

# Отключаем буферизацию stdout/stderr и создание .pyc
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# psycopg[binary] не требует gcc/libpq-dev — образ меньше
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Отдельный непривилегированный пользователь
RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --no-create-home app

COPY --chown=app:app . .

USER app

EXPOSE 5000

# Gunicorn: 2 воркера, bind на все интерфейсы, лог в stdout
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "run:app"]