import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Categoria(Base):
    __tablename__ = 'categoria'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250), nullable=False)
    user = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'nome': self.nome,
            'id': self.id,
        }


class Item(Base):
    __tablename__ = 'item'

    nome = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    descricao = Column(String(250))
    categoria_id = Column(Integer, ForeignKey('categoria.id'))
    categoria = relationship(Categoria)
    user = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'nome': self.nome,
            'descricao': self.descricao,
            'id': self.id
        }


engine = create_engine('sqlite:///catalogo.db')


Base.metadata.create_all(engine)
