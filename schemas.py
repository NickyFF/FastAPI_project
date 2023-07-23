from numbers import Number
from typing import List, Optional
import uuid
from pydantic import BaseModel, condecimal
from uuid import UUID

class DishBase(BaseModel):
    title: str
    price: condecimal(decimal_places=2, max_digits=10)
    description: str

class DishCreate(DishBase):
    pass

class DishUpdate(DishBase):
    pass

class Dish(DishBase):
    id: UUID
    submenu_id: UUID

    class Config:
        from_attributes = True


class SubmenuBase(BaseModel):
    title: str
    description: Optional[str]
    

class SubmenuCreate(SubmenuBase):
    pass

class SubmenuUpdate(SubmenuBase):
    pass


class Submenu(SubmenuBase):
    id: UUID
    menu_id: UUID

    class Config:
        from_attributes = True

class SubmenuWithDishCount(Submenu):
    dishes_count: int

    class Config:
        from_attributes = True

class MenuBase(BaseModel):
    title: str
    description: str

class MenuCreate(MenuBase):
    pass

class MenuUpdate(MenuBase):
    pass

class Menu(MenuBase):
    id: UUID

    class Config:
        from_attributes = True

class MenuWithCounts(Menu):
    submenus_count: int
    dishes_count: int

    class Config:
        from_attributes = True



