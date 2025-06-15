# Introdução

O objetivo deste desafio é avaliar seus conhecimentos em APIs, Webhooks e arquiteturas assíncronas, além da sua capacidade de projetar soluções inteligentes usando Django, Django Rest Framework (DRF) e Celery. Você deverá desenvolver uma web API que sincroniza eventos de um sistema de atendimentos via WhatsApp, processa mensagens de usuários e gera respostas automáticas.

---

# 🎯 O Desafio

Desenvolver uma web API utilizando Django Rest Framework que receba eventos de conversa e mensagem (webhooks), armazene-os em um banco PostgreSQL, processe mensagens de forma assíncrona com Celery (usando Redis como broker). A partir desse processamento, o sistema deve gerar mensagens de resposta ("OUTBOUND") que serão exibidas quando o usuário consultar a conversa, via endpoint.

---

# 📌 Requisitos

1. **Criar dois modelos principais no Django:**
   - Conversation
   - Message (relacionado a Conversation)

2. **Endpoint principal:**
   - POST `/webhook/`
   - Recebe eventos JSON (descritos abaixo)
   - Valida payloads e retorna códigos HTTP apropriados

3. **Endpoint de consulta:**
   - GET `/conversations/{id}/`
   - Retorna detalhes da conversa:
     - `id`, `status`, `created_at`, `updated_at`
     - Lista de mensagens associadas (campos: `id`, `type`, `content`, `timestamp`)

4. **Banco de dados:**
   - PostgreSQL (rodando em container Docker)

5. **Broker/Cache para Celery:**
   - Redis (rodando em container Docker)

6. **Processamento assíncrono:**
   - Celery executando tasks de processamento de mensagens

7. **Docker & Docker Compose:**
   - O projeto deve incluir docker-compose.yml orquestrando os seguintes serviços:
     - Django (gunicorn + django)
     - Celery (worker)
     - PostgreSQL
     - Redis

---

# 📦 Formato dos Webhooks

A API receberá eventos via POST em /webhook/, com JSON nos formatos:

## 1. NEW_CONVERSATION
Cria uma nova conversa (estado inicial: `OPEN`).

```json
{
  "type": "NEW_CONVERSATION",
  "timestamp": "2025-06-04T14:20:00Z",
  "data": {
    "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
  }
}
```

## 2. NEW_MESSAGE
Nova mensagem enviada por usuário (sempre `type`: `USER`).

```json
{
  "type": "NEW_MESSAGE",
  "timestamp": "2025-06-04T14:20:05Z",
  "data": {
    "id": "49108c71-4dca-4af3-9f32-61bc745926e2",
    "content": "Olá, quero informações sobre alugar um apartamento.",
    "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
  }
}
```

## 3. CLOSE_CONVERSATION
Fecha a conversa (estado passa a CLOSED).

```json
{
  "type": "CLOSE_CONVERSATION",
  "timestamp": "2025-06-04T14:25:00Z",
  "data": {
    "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
  }
}
```

---

# 📌 Regras de Negócio

## 1. Estados de Conversation
- Ao criar, status = OPEN.
- Depois de fechado, status = CLOSED; conversas fechadas não aceitam novas mensagens (NEW_MESSAGE retorna HTTP 400).

## 2. Mensagens (Message)
- **Tipos permitidos:**
  - "INBOUND": mensagens recebidas pela API/Webhook (payload)
  - "OUTBOUND": gerado internamente pela aplicação
- **Cada Message tem:**
  - id (UUID) – único
  - conversation_id (FK)
  - type: "INBOUND" ou "OUTBOUND"
  - content (texto)
  - timestamp (DateTime do evento)
  - campos adicionais a seu critério, se achar necessário.

## 3. Retorno dos endpoints
- Payloads inválidos (formato incorreto, regras de negócio violadas) devem retornar `HTTP 400 Bad Request`
- Payloads de mensagem válidos devem retornar `HTTP 202 Accepted` e iniciar o processamento assíncrono via Celery task
- Retornos esperados:
  - **NEW_CONVERSATION:**
    - 201 Created (sucesso)
    - 400 Bad Request (se ID já existir)
  - **NEW_MESSAGE:**
    - 202 Accepted (se payload válido, processo assíncrono agendado ou bufferizado)
    - 400 Bad Request (se conversa fechada, payload inválido ou buffer expirado)
  - **CLOSE_CONVERSATION:**
    - 200 OK (sucesso)
    - 400 Bad Request (se conversa não existir ou já fechada)
  - **GET /conversations/{id}:**
    - 200 OK (sucesso, retorna JSON da conversa)
    - 404 Not Found (não existe)


## 4. Mensagens fora de ordem
- A aplicação deve tolerar uma breve falta de sincronia no recebimento de webhooks
  - Por exemplo, uma NEW_MESSAGE que faz referência a uma `Conversation` que ainda não foi criada, pois o NEW_CONVERSATION ainda não chegou
  - O limite deve ser de, no máximo, 6 segundos

**Exemplo de tempos:**
- T=0s: Chega NEW_MESSAGE (`id=abc`) para `conversation_id=123`
- T=2s: Chega NEW_CONVERSATION com `id=123` (dentro do limite de 6s)
- T=7s: Chega NEW_MESSAGE (`id=dce`) para `conversation_id=456`
- T=15s: Chega NEW_CONVERSATION com `id=456`

- Neste cenário, a mensagem com id `abc` deverá ser incluída na conversa com id `123` e ser processada normalmente. Porém, a mensagem com id `dce` é inválida e não deveria ser processada, pois ultrapassou o período limite de tolerância de 6s.

## 5. Processamento de múltiplas mensagens do usuário
- Na vida real, seres humanos podem "quebrar" a sua comunicação em várias mensagens

- **Exemplo de fluxo**:
  - T=0s: "Oi!"
  - T=2s: "Estou buscando uma casa"
  - T=4s: "Com 2 quartos para morar!"

- A aplicação deve garantir que se um usuário enviar apenas UMA mensagem, ela será processada normalmente.
- Porém, caso o usuário envie várias mensagens em sequência rápida (intervalo de até 5 segundos entre elas), essas mensagens devem ser agrupadas e processadas juntamente, gerando apenas uma mensagem (type `OUTBOUND`).

Ou seja:
- Quando um usuário enviar UMA mensagem, deve ser processada sozinha.
- Se o usuário enviar várias mensagens em sequência rápida (intervalo de até 5 segundos entre elas), essas mensagens devem ser agrupadas em um único job assíncrono, evitando múltiplas respostas redundantes.

- **Exemplo de fluxo:**
  1. T=0s: chega "Oi"
  2. T=2s: chega "Tudo bem?"
  3. T=5s: chega "Quero alugar imóvel."
  4. Se nenhuma mensagem nova chegar antes de T=10s, processe as três juntas e gere uma resposta única.

## 6. Geração de Resposta

O processamento de mensagens realizado pelo Celery deve **gerar automaticamente uma nova mensagem do tipo `OUTBOUND`**, que será armazenada no banco de dados e vinculada à mesma conversa das mensagens recebidas.

A resposta `OUTBOUND` deve conter um **conteúdo (`content`) padrão que lista os IDs das mensagens recebidas** no agrupamento. O conteúdo deve seguir o seguinte formato:

```python
"""Mensagens recebidas:\n{id-1}\n{id-2}"""
```

### Exemplos

**Caso 1 – Mensagem única**

Se a aplicação receber uma única mensagem INBOUND no período de 5s com o `id`:
- 55ebb68a-a8ef-47d4-9a28-c97e0f0ec8f1

A mensagem `OUTBOUND` gerada deverá ter o seguinte conteúdo:
```python
"""Mensagens recebidas:
55ebb68a-a8ef-47d4-9a28-c97e0f0ec8f1
"""
```

**Caso 2 – Múltiplas mensagens agrupadas**

Se a aplicação receber três mensagens INBOUND em sequência rápida (com até 5 segundos entre cada uma), com os seguintes `ids`:
- 55ebb68a-a8ef-47d4-9a28-c97e0f0ec8f1  
- 8d41e347-da5f-4d03-8377-4378d86cfcf0  
- 1f9e918a-6d32-4a75-93a7-34b9e0faff22  

A mensagem `OUTBOUND` gerada deverá ter o seguinte conteúdo:

```python
"""Mensagens recebidas:
55ebb68a-a8ef-47d4-9a28-c97e0f0ec8f1
8d41e347-da5f-4d03-8377-4378d86cfcf0
1f9e918a-6d32-4a75-93a7-34b9e0faff22
"""
```

## 7. Fechamento de Conversa
- O evento CLOSE_CONVERSATION marca status = CLOSED.

---

# 🔥 Bônus (Opcional)

- Frontend simples (Vue.js) para visualizar conversas.
- Documentar o desenho da arquitetura (diagramas mermaid ou MIRO).

Valorizamos entregas além do mínimo!

---

# 🚀 Tecnologias e Ferramentas

## Linguagem/Framework:
- Python 3.10+
- Django
- Django Rest Framework

## Processamento Assíncrono:
- Celery
- Redis (broker e/ou backend de resultados)

## Banco de Dados:
- PostgreSQL

## Containerização:
- Docker
- docker-compose

## 📌 Instruções de Instalação

### Pré-requisitos

- Docker e Docker Compose instalados
- Git

### Instalação do Projeto

> [!WARNING]  
> Siga todas as instruções de instalação do projeto. O descumprimento dos requisitos de instalação acarretará a desclassificação do(a) candidato(a).

1. Crie um repositório público, utilizando este repositório como template. Para isso, clique sobre o botão "**Use this template**", no canto superior direito desta tela. Forks **não** serão aceitos.

2. Preencha o arquivo env.example com as variáveis de ambiente necessárias.

3. Crie um arquivo INSTRUCTIONS.md com as instruções para rodar o projeto.


# 📌 Entrega e Requisitos

## Envio do link do repositório:
Após concluir, envie o link para tecnologia@realmate.com.br, incluindo no corpo do e-mail:
- Seu nome completo
- Seu número de WhatsApp

---

# 📚 Referências

- [Django Rest Framework](https://www.django-rest-framework.org/)
- [Django](https://www.djangoproject.com/)
- [Celery](https://docs.celeryproject.org/)
- [Redis](https://redis.io/)

---

# 📧 Dúvidas

Caso tenha dúvidas sobre o desafio, entre em contato com nossa equipe de tecnologia pelo WhatsApp!

Boa sorte! 🚀