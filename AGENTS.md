# Guia para Agentes (Codex)

Escopo: todo o repositório.

## Padrões de Código
- Siga PEP 8.
- Use type hints em funções públicas.
- Inclua docstrings concisas em módulos, classes e funções.
- Evite abreviações não óbvias; nomes descritivos.

## Estrutura do Projeto
- `app/database.py`: engine, sessão e Base do SQLAlchemy; `get_db()` como dependency.
- `app/models.py`: modelos ORM do SQLAlchemy.
- `app/schemas.py`: schemas Pydantic (v2) com validações.
- `app/main.py`: instância FastAPI e rotas.

## Convenções FastAPI
- Rotas com `tags=["Tasks"]`.
- Use `HTTPException` com códigos adequados (404 quando não encontrado).
- Utilize dependency injection com `Depends(get_db)`.
- Crie tabelas no evento de `startup`.

## Padrões de Validação
- Utilize `pydantic.Field` para `min_length`, `max_length`, etc.
- Schemas de resposta devem usar `from_attributes=True` para mapear ORM.
- Atualizações (`PUT`) aceitam todos os campos opcionais.

