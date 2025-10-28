# Task Management API (FastAPI)

API de gerenciamento de tarefas construída com FastAPI, SQLAlchemy e SQLite. Inclui endpoints CRUD completos, validação com Pydantic e documentação automática via OpenAPI (/docs).

## Tecnologias
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic v2
- SQLite

## Estrutura do Projeto

```
app/
  __init__.py
  database.py
  models.py
  schemas.py
  main.py
.gitignore
requirements.txt
README.md
AGENTS.md
.coderabbit.yaml
```

## Setup

1. Clone o repositório
   - `git clone <URL_DO_REPO>`
   - `cd api_review_aovivo`

2. Crie e ative um ambiente virtual (recomendado)
   - Windows (PowerShell):
     - `python -m venv venv`
     - `./venv/Scripts/Activate.ps1`
   - Linux/macOS:
     - `python3 -m venv venv`
     - `source venv/bin/activate`

3. Instale as dependências
   - `pip install -r requirements.txt`

4. Rode a aplicação
   - `uvicorn app.main:app --reload`
   - Acesse: `http://localhost:8000`

## Documentação e Testes Rápidos

- Documentação interativa: `http://localhost:8000/docs`
- Esquema OpenAPI: `http://localhost:8000/openapi.json`

## Endpoints Principais

- `GET /` — Mensagem de boas-vindas
- `POST /tasks/` — Cria uma tarefa
- `GET /tasks/` — Lista tarefas com paginação e filtro opcional por `completed`
- `GET /tasks/{task_id}` — Busca tarefa por ID
- `PUT /tasks/{task_id}` — Atualiza tarefa
- `DELETE /tasks/{task_id}` — Remove tarefa

## Exemplos de Requisição (curl)

- Criar tarefa
  - 
    ```bash
    curl -X 'POST' \
      'http://localhost:8000/tasks/' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "title": "teste",
      "description": "testando"
    }'
    ```

- Listar tarefas (10 primeiras)
  - 
    ```bash
    curl -X 'GET' \
      'http://localhost:8000/tasks/?skip=0&limit=10' \
      -H 'accept: application/json'
    ```

- Listar tarefas concluídas
  - 
    ```bash
    curl -X 'GET' \
      'http://localhost:8000/tasks/?completed=true' \
      -H 'accept: application/json'
    ```

- Buscar por ID
  - 
    ```bash
    curl -X 'GET' \
      'http://localhost:8000/tasks/1' \
      -H 'accept: application/json'
    ```

- Atualizar tarefa
  - 
    ```bash
    curl -X 'PUT' \
      'http://localhost:8000/tasks/1' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "title": "novo titulo",
      "description": "nova descricao",
      "completed": true
    }'
    ```

- Remover tarefa
  - 
    ```bash
    curl -X 'DELETE' \
      'http://localhost:8000/tasks/1' \
      -H 'accept: application/json' -i
    ```

## Notas

- O banco de dados SQLite é criado localmente em `tasks.db`.
- Os modelos Pydantic utilizam `from_attributes=True` (Pydantic v2) para conversão a partir de objetos ORM.




## Prompt para criar o projeto

```markdown
Criar projeto FastAPI completo do zero com API de gerenciamento de tarefas.

ESTRUTURA DE ARQUIVOS:
- app/__init__.py (vazio, marca como pacote)
- app/main.py (aplicação FastAPI)
- app/database.py (configuração SQLite)
- app/models.py (modelos SQLAlchemy)
- app/schemas.py (schemas Pydantic)
- .gitignore (incluir: venv/, __pycache__/, *.db, .env, .vscode/)
- requirements.txt
- README.md (com instruções completas de setup e uso)
- AGENTS.md (padrões de código do projeto)
- .coderabbit.yaml (configuração CodeRabbit em português)

DEPENDÊNCIAS A INSTALAR:
- fastapi
- uvicorn[standard]
- sqlalchemy
- pydantic

IMPLEMENTAÇÃO DETALHADA:

1. app/database.py:
   - SQLAlchemy engine com SQLite (arquivo tasks.db)
   - URL: sqlite:///./tasks.db
   - SessionLocal com sessionmaker(autocommit=False, autoflush=False)
   - Base = declarative_base()
   - Função get_db() para dependency injection com yield

2. app/models.py:
   - Importar Base de app.database
   - Classe Task(Base) com __tablename__ = "tasks"
   - Campos: id (Integer, primary_key, index), title (String, nullable=False, index), 
     description (String), completed (Boolean, default=False), 
     created_at (DateTime, default=datetime.utcnow)

3. app/schemas.py:
   - TaskCreate: title (Field min_length=3, max_length=100), 
     description (Optional, max_length=500)
   - TaskUpdate: todos campos Optional
   - TaskResponse: todos campos + from_attributes=True (Pydantic v2)

4. app/main.py:
   - FastAPI(title="Task Management API", description="...", version="1.0.0")
   - models.Base.metadata.create_all(bind=engine) no startup
   - Endpoints CRUD completos com tags=["Tasks"]:
     * POST /tasks/ (response_model=TaskResponse, status_code=201)
     * GET /tasks/ (List[TaskResponse], params: skip=0, limit=10, completed: Optional[bool])
     * GET /tasks/{task_id} (TaskResponse)
     * PUT /tasks/{task_id} (TaskResponse)
     * DELETE /tasks/{task_id} (status_code=204)
   - Tratamento HTTPException 404 para task não encontrada
   - Docstrings em todas as funções
   - Endpoint raiz GET / retorna mensagem de boas-vindas

5. README.md incluir:
   - Descrição do projeto
   - Tecnologias usadas
   - Instruções de setup (clonar, venv, instalar, rodar)
   - Como testar a API (via /docs)
   - Exemplos de requisições

6. AGENTS.md incluir:
   - Padrões Python (PEP 8, type hints, docstrings)
   - Estrutura do projeto
   - Convenções FastAPI
   - Padrões de validação

7. .coderabbit.yaml:
   - language: "pt"
   - reviews.high_level_summary: true
   - path_filters para ignorar venv/, __pycache__/, *.db
   - path_instructions específicas para app/models.py, app/schemas.py, app/main.py

APÓS CRIAR TODOS OS ARQUIVOS:
1. Executar: pip install -r requirements.txt
2. Confirmar que todas dependências foram instaladas
3. Informar que o projeto está pronto para rodar com: uvicorn app.main:app --reload
```
