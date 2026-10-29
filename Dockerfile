FROM python:3.13-slim@sha256:57b29a7c050c4e679e4bea572e14b3965cf4b5839de2da49d55e49ffc4024f39

# Отключаем буферизацию stdout/stderr и создание .pyc
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# psycopg[binary] не требует gcc/libpq-dev — образ меньше
COPY requirements-prod.lock .
RUN pip install --no-cache-dir -r requirements-prod.lock

# Отдельный непривилегированный пользователь
RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --no-create-home app

COPY --chown=app:app . .

USER app

EXPOSE 5000

# Gunicorn: 2 воркера, bind на все интерфейсы, лог в stdout
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "run:app"]

#Слой — это набор изменений в файловой системе, который создаётся при выполнении инструкции Dockerfile.

# RUN apt-get install python — создаёт файлы → слой = эти файлы

# RUN pip install flask — создаёт файлы → слой = эти файлы

# ENV PATH=/usr/bin — ничего не создаёт → слоя нет

# CMD ["gunicorn"] — ничего не создаёт → слоя нет

# USER app — ничего не создаёт → слоя нет

# WORKDIR /app — создаёт папку → слой = эта папка (8 KB)

# COPY . . — копирует файлы → слой = скопированные файлы
