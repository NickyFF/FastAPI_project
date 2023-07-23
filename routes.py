from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud, schemas
from typing import List
from config import SessionLocal
from models import Menu
from fastapi.param_functions import Path

router = APIRouter()

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Меню (Menu) - CRUD операции

@router.post("/menus/", response_model=schemas.Menu, status_code=201)
def create_menu(menu: schemas.MenuCreate, db: Session = Depends(get_db)):
    # Проверка на успешное создание меню 
    return crud.create_menu(db, menu)

@router.get("/menus/", response_model=list[schemas.MenuWithCounts])
def read_menus(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    menus = crud.get_menus(db, skip=skip, limit=limit)
    return [
        {
            "id": menu.id,
            "title": menu.title,
            "description": menu.description,
            "submenus_count": len(menu.submenus),
            "dishes_count": sum(len(submenu.dishes) for submenu in menu.submenus)
        }
        for menu in menus
    ]

@router.get("/menus/{menu_id}", response_model=schemas.MenuWithCounts)
def read_menu(menu_id: UUID, db: Session = Depends(get_db)):
    menu = crud.get_menu_by_id(db, menu_id)
    if menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    return {
        "id": menu.id,
        "title": menu.title,
        "description": menu.description,
        "submenus_count": len(menu.submenus),
        "dishes_count": sum(len(submenu.dishes) for submenu in menu.submenus)
    }

@router.patch("/menus/{menu_id}", response_model=schemas.Menu)
def update_menu(menu_id: UUID, menu_update: schemas.MenuUpdate, db: Session = Depends(get_db)):
    menu = crud.get_menu_by_id(db, menu_id)
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    return crud.update_menu(db, menu=menu, menu_update=menu_update)

@router.delete("/menus/{menu_id}", status_code=200)
def delete_menu(menu_id: UUID, db: Session = Depends(get_db)):
    return crud.delete_menu(db, menu_id)

# Подменю (Submenu) - CRUD операции

@router.get("/menus/{menu_id}/submenus", response_model=List[schemas.Submenu])
def read_submenus(menu_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    submenus = crud.get_submenus_by_menu(db, menu_id=menu_id, skip=skip, limit=limit)
    return [
        {
            "id": submenu.id,
            "title": submenu.title,
            "description": submenu.description,
            "menu_id": submenu.menu_id,
            "dishes_count": sum(len(submenu.dishes) for submenu in submenus)
        }
        for submenu in submenus
    ]

@router.post("/menus/{menu_id}/submenus", response_model=schemas.Submenu, status_code=201)
def create_submenu_for_menu(menu_id: UUID, submenu: schemas.SubmenuCreate, db: Session = Depends(get_db)):
    menu = crud.get_menu_by_id(db, menu_id)
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    return crud.create_submenu(db, submenu=submenu, menu_id=menu_id)

@router.get("/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.SubmenuWithDishCount)
def read_submenu(submenu_id: UUID, menu_id: UUID, db: Session = Depends(get_db)):
    menu = crud.get_menu_by_id(db, menu_id)
    submenu = crud.get_submenu_by_id(db, submenu_id)
    if submenu is None:
        raise HTTPException(status_code=404, detail="submenu not found")
    return {
        "id": submenu.id,
        "title": submenu.title,
        "menu_id": menu.id,
        "description": submenu.description,
        "dishes_count": len(submenu.dishes)
    }

@router.patch("/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.Submenu)
def update_submenu(menu_id: UUID, submenu_id: UUID, submenu_update: schemas.SubmenuUpdate, db: Session = Depends(get_db)):
    menu = crud.get_menu_by_id(db, menu_id)
    submenu = crud.get_submenu_by_id(db, submenu_id)
    if submenu is None:
        raise HTTPException(status_code=404, detail="Submenu not found")
    updated_submenu = crud.update_submenu(db, submenu=submenu, submenu_update=submenu_update)
    return updated_submenu

@router.delete("/menus/{menu_id}/submenus/{submenu_id}", response_model=dict)
def delete_submenu(submenu_id: UUID, db: Session = Depends(get_db)):
    submenu = crud.get_submenu_by_id(db, submenu_id)
    if submenu is None:
        raise HTTPException(status_code=404, detail="Submenu not found")
    crud.delete_submenu(db, submenu_id=submenu_id)
    return {"message": "Submenu deleted successfully"}

# Блюдо (Dish) - CRUD операции

@router.post("/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=schemas.Dish, status_code=201)
def create_dish_for_submenu(submenu_id: UUID, dish: schemas.DishCreate, db: Session = Depends(get_db)):
    submenu = crud.get_submenu_by_id(db, submenu_id)
    if submenu is None:
        raise HTTPException(status_code=404, detail="Submenu not found")
    created_dish = crud.create_dish(db, dish=dish, submenu_id=submenu_id)
    if created_dish is None:
        raise HTTPException(status_code=400, detail="Dish with this name already exists in the submenu")
    return {
        "id": created_dish.id,
        "title": created_dish.title,
        "price": created_dish.price,
        "description": created_dish.description, 
        "submenu_id": created_dish.submenu_id
    }

@router.get("/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=List[schemas.Dish])
def read_dishes(submenu_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    submenu = crud.get_submenu_by_id(db, submenu_id)
    dishes = crud.get_dishes_by_submenu(db, submenu_id=submenu_id, skip=skip, limit=limit)
    return dishes

@router.get("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=schemas.Dish)
def read_dish(submenu_id: UUID, dish_id: UUID, db: Session = Depends(get_db)):
    submenu = crud.get_submenu_by_id(db, submenu_id)
    dish = crud.get_dish_by_id(db, dish_id)
    if dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    return {
        "id": dish.id,
        "title": dish.title,
        "description": dish.description,
        "price": dish.price,
        "submenu_id": dish.submenu_id
    }

@router.patch("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=schemas.Dish)
def update_dish(submenu_id: UUID, dish_id: UUID, dish_update: schemas.DishUpdate, db: Session = Depends(get_db)):
    submenu = crud.get_submenu_by_id(db, submenu_id)
    dish = crud.get_dish_by_id(db, dish_id)
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")

    updated_dish = crud.update_dish(db, dish=dish, dish_update=dish_update)
    return updated_dish

@router.delete("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=dict)
def delete_dish(dish_id: UUID, db: Session = Depends(get_db)):
    dish = crud.get_dish_by_id(db, dish_id)
    if dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    db.delete(dish)
    db.commit()
    return {"message": "dish deleted successfully"}