import uuid
from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from config import Base

class Menu(Base):
    __tablename__ = "menus"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, unique=True, index=True)
    description = Column(String)
    submenus = relationship("Submenu", back_populates="menu", cascade="all, delete-orphan")

class Submenu(Base):
    __tablename__ = "submenus"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, index=True)
    description = Column(String)
    menu_id = Column(UUID(as_uuid=True), ForeignKey("menus.id"))
    menu = relationship("Menu", back_populates="submenus")
    dishes = relationship("Dish", back_populates="submenu", cascade="all, delete-orphan")

class Dish(Base):
    __tablename__ = "dishes"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, index=True)
    description = Column(String)
    price = Column(Numeric(precision=10, scale=2))
    submenu_id = Column(UUID(as_uuid=True), ForeignKey("submenus.id"))
    submenu = relationship("Submenu", back_populates="dishes")