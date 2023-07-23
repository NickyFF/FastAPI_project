import uuid
from sqlalchemy.orm import Session
from models import Menu, Submenu, Dish
from schemas import MenuCreate, SubmenuCreate, DishCreate, MenuUpdate, SubmenuUpdate, DishUpdate
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException, status
from uuid import UUID

# Получение меню по его ID
def get_menu_by_id(db: Session, menu_id: uuid.UUID):
    return db.query(Menu).filter(Menu.id == menu_id).first()

# Получение всех меню
def get_menus(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Menu).offset(skip).limit(limit).all()

# Создание нового меню
def create_menu(db: Session, menu: MenuCreate):
    db_menu = Menu(title=menu.title, description=menu.description, id=uuid.uuid4().hex)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return {
        "id": db_menu.id,
        "title": db_menu.title,
        "description": db_menu.description
    }
# Получение подменю по его ID
def get_submenu_by_id(db: Session, submenu_id: uuid.UUID):
    return db.query(Submenu).filter(Submenu.id == submenu_id).first()

# Изменение объекта меню
def update_menu(db: Session, menu: Menu, menu_update: MenuUpdate):
    for key, value in menu_update.dict(exclude_unset=True).items():
        setattr(menu, key, value)
    db.commit()
    db.refresh(menu)
    return menu

# Получение всех подменю в заданном меню
def get_submenus_by_menu(db: Session, menu_id: UUID, skip: int = 0, limit: int = 100):
    return db.query(Submenu).filter(Submenu.menu_id == menu_id).offset(skip).limit(limit).all()

# Создание нового подменю в заданном меню
def create_submenu(db: Session, submenu: SubmenuCreate, menu_id: uuid.UUID):
    db_submenu = Submenu(title=submenu.title, menu_id=menu_id, description=submenu.description, id=uuid.uuid4().hex)
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    return db_submenu

def update_submenu(db: Session, submenu: Submenu, submenu_update: SubmenuUpdate):
    for key, value in submenu_update.dict(exclude_unset=True).items():
        setattr(submenu, key, value)
    db.commit()
    db.refresh(submenu)
    return submenu

# Получение блюда по его ID
def get_dish_by_id(db: Session, dish_id: uuid.UUID):
    return db.query(Dish).filter(Dish.id == dish_id).first()

# Получение всех блюд в заданном подменю
def get_dishes_by_submenu(db: Session, submenu_id: uuid.UUID, skip: int = 0, limit: int = 100):
    return db.query(Dish).filter(Dish.submenu_id == submenu_id).offset(skip).limit(limit).all()

# Создание нового блюда в заданном подменю
def create_dish(db: Session, dish: DishCreate, submenu_id: uuid.UUID):
    # Проверяем, что блюдо не привязано к другому подменю
    try:
        if db.query(Dish).filter(Dish.submenu_id == submenu_id, Dish.title == dish.title).first():
            return None

        db_dish = Dish(title=dish.title, description=dish.description, price=dish.price, submenu_id=submenu_id, id=uuid.uuid4().hex)
        db.add(db_dish)
        db.commit()
        db.refresh(db_dish)
        return db_dish
    except RequestValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())

def update_dish(db: Session, dish: Dish, dish_update: DishUpdate):
    for key, value in dish_update.dict(exclude_unset=True).items():
        setattr(dish, key, value)
    db.commit()
    db.refresh(dish)
    return dish

# Удаление меню по его ID со всеми подменю и блюдами
def delete_menu(db: Session, menu_id: uuid.UUID):
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if menu:
        db.delete(menu)
        db.commit()
        return "Success answer"
    return False

# Удаление подменю по его ID со всеми блюдами
def delete_submenu(db: Session, submenu_id: uuid.UUID):
    db.query(Dish).filter(Dish.submenu_id == submenu_id).delete(synchronize_session=False)
    db.query(Submenu).filter(Submenu.id == submenu_id).delete(synchronize_session=False)
    db.commit()
    return True