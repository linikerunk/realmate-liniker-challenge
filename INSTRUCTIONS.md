# Instruções de Configuração do Projeto

## 1. Instalação do UV (Gerenciador de Pacotes Python)

Primeiro, instale o UV usando um dos seguintes comandos:

```bash
# Via curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Via pip
pip install uv
```

## 2. Configuração do Ambiente Virtual

```bash
# Criar ambiente virtual
uv venv .venv

# Ativar o ambiente virtual
source .venv/bin/activate
```

## 3. Instalação das Dependências

Com o ambiente virtual ativado, instale as dependências do projeto:

```bash
uv pip install --requirements requirements.txt
```

## 4. Configuração do Django

```bash
# Executar migrações
python manage.py migrate

# Criar superusuário (opcional)
python manage.py createsuperuser

# Rodar o servidor de desenvolvimento
python manage.py runserver
```

## 5. Configuração do Celery

```bash
# Em um terminal separado (com o ambiente virtual ativado)
celery -A realmate_challenge worker -l info
```

## Estrutura do Projeto

O projeto utiliza:
- Django 5.1+
- Django REST Framework
- Celery para tarefas assíncronas
- PostgreSQL como banco de dados
- Redis como message broker para o Celery

## Comandos Úteis do UV

```bash
# Instalar um novo pacote
uv pip install nome-do-pacote

# Atualizar dependências
uv pip install --upgrade --requirements requirements.txt

# Listar pacotes instalados
uv pip list

# Desativar ambiente virtual
deactivate
```

## Observações
- Mantenha o ambiente virtual sempre ativado durante o desenvolvimento
- Certifique-se de que o PostgreSQL e Redis estejam rodando antes de iniciar o projeto
- Configure as variáveis de ambiente necessárias no arquivo `.env` (use `env.example` como referência)
