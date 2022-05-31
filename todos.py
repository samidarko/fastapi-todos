from typing import List, Union
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class CreateTodo(BaseModel):
    name: str


class Todo(CreateTodo):
    id: UUID
    is_completed: bool


todos: List[Todo] = []


def get_todo_index(todo_id: UUID) -> int:
    for i, todo in enumerate(todos):
        if todo.id == todo_id:
            return i
    return -1


@app.get("/")
def read_root():
    return {"Hello": "Databook"}


@app.get(
    "/todos",
    summary="todos list",
    response_model=List[Todo],
)
def list_todo(is_completed: Union[bool, None] = None):
    def predicate(todo):
        if is_completed is None:
            return True
        return todo.is_completed == is_completed

    return [todo for todo in todos if predicate(todo)]


@app.post(
    "/todos",
    summary="todo create",
    response_model=Todo,
)
def create_todo(payload: CreateTodo):
    todo = Todo(id=uuid4(), name=payload.name, is_completed=False)
    todos.append(todo)
    return todo


@app.get(
    "/todos/{todo_id}",
    summary="todo read",
    response_model=Todo,
)
def read_todo(todo_id: UUID):
    index = get_todo_index(todo_id)
    if index < 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    return todos[index]


@app.put(
    "/todos/{todo_id}",
    summary="todo update",
    response_model=Todo,
)
def update_todo(todo_id: UUID, payload: CreateTodo):
    index = get_todo_index(todo_id)
    if index < 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    global todos
    todos[index].name = payload.name
    return todos[index]


@app.put(
    "/todos/{todo_id}/toggle",
    summary="todo toggle completed status",
    response_model=Todo,
)
def toggle_todo(todo_id: UUID):
    index = get_todo_index(todo_id)
    if index < 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    global todos
    todos[index].is_completed = not todos[index].is_completed
    return todos[index]


@app.delete(
    "/todos/{todo_id}", summary="todo delete", status_code=status.HTTP_204_NO_CONTENT
)
def delete_todo(todo_id: UUID):
    global todos
    todos = [todo for todo in todos if todo.id != todo_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/secure/todos/{todo_id}",
    summary="secure todo read",
    response_model=Todo,
    dependencies=[Depends(oauth2_scheme)],
    tags=["auth"],
)
def secure_read_todo(todo_id: UUID):
    index = get_todo_index(todo_id)
    if index < 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    return todos[index]
