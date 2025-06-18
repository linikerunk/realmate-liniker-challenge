# Imagem base
FROM python:3.12-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Diretório de trabalho
WORKDIR /app

# Instalar o 'uv'
RUN pip install uv

# Copiar arquivos de dependência
COPY requirements.txt requirements.txt
COPY requirements.in requirements.in

# Instalar dependências
RUN uv pip sync --system requirements.txt

# Copiar tudo, inclusive o entrypoint
COPY . .

# Garantir permissão de execução do script
RUN chmod +x /app/entrypoint.sh

# Expor porta
EXPOSE 8000

# Definir entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]