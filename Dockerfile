FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN pip install uv

# Copiar arquivos do projeto
COPY requirements.txt .
COPY pyproject.toml .

# Instalar dependências Python
RUN uv pip install --system -r requirements.txt

COPY . .

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput
