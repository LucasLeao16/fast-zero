from http import HTTPStatus

from fastapi import FastAPI

from fast_zero.routers import auth, todos, users

app = FastAPI()

# Cada router agrupa as rotas de um recurso (/users, /auth, /todos)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)


@app.get("/", status_code=HTTPStatus.OK)
def read_root():
    return {"message": "Olá mundo"}
