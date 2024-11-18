# Задача "Маршрутизация заданий":

# Необходимо описать логику функций в task.py используя ранее написанные маршруты FastAPI.

# Делается практически идентично users.py с некоторыми дополнениями.

# Напишите логику работы функций маршрутов аналогично предыдущему заданию:

# В модуле task.py:

# Функция all_tasks ('/') - идентично all_users.
# Функция task_by_id ('/task_id') - идентично user_by_id.

# Функция craete_task ('/create'):
# Дополнительно принимает модель CreateTask и user_id.
# Подставляет в таблицу Task запись значениями указанными в CreateTask и user_id, если пользователь найден.
# Т.е. при создании записи Task вам необходимо связать её с конкретным пользователем User.
# В конце возвращает словарь {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}
# В случае отсутствия пользователя выбрасывает исключение с кодом 404 и описанием "User was not found"

# Функция update_task ('/update') - идентично update_user.
# Функция delete_task ('/delete') - идентично delete_user.

# В модуле user.py:
# Создайте новый маршрут get "/user_id/tasks" и функцию tasks_by_user_id. Логика этой функции должна заключатся
# в возврате всех Task конкретного User по id.
# Дополните функцию delete_user так, чтобы вместе с пользователем удалялись все записи связанные с ним.

from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from slugify import slugify
from sqlalchemy import insert, update, delete, select
from sqlalchemy.orm import Session

from backend.db_depends import get_db
from models import User, Task
from schemas import CreateTask, UpdateTask

router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Task was not found')
    return task


@router.post('/create')
async def create_task(db: Annotated[Session, Depends(get_db)], create_task_models: CreateTask, user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found')
    db.execute(insert(Task).values(title=create_task_models.title,
                                   content=create_task_models.content,
                                   priority=create_task_models.priority,
                                   user_id=user_id,
                                   slug=slugify(create_task_models.title)))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int, update_task_models: UpdateTask):
    task_update = db.scalar(select(Task).where(Task.id == task_id))
    if task_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    db.execute(update(Task).where(Task.id == task_id).values(title=update_task_models.title,
                                                             content=update_task_models.content,
                                                             priority=update_task_models.priority,
                                                             slug=slugify(update_task_models.title)))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}


@router.delete('/delete')
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task_delete = db.scalar(select(Task).where(Task.id == task_id))
    if task_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Task delete is successful!'}
