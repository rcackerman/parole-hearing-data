import os

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy import create_engine, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import UnmappedInstanceError


_connected = False
_engine = None
_session_factory = None

ModelBase = declarative_base()


def connect_db(url):
    global _connected, _engine, _session_factory

    if not _connected:
        _engine = create_engine(url)
        _session_factory = scoped_session(
            sessionmaker(autocommit=False, autoflush=True, bind=_engine))
        ModelBase.query = _session_factory.query_property()
        _connected = True

    return _engine


def session():
    global _session_factory
    return _session_factory()


class Base(object):

    def __repr__(self):
        return '{0}({1!r})'.format(self.__class__.__name__, vars(self))

    @classmethod
    def create(kls, **kwargs):
        sess = session()
        inst = kls(**kwargs)
        sess.add(inst)
        try:
            sess.commit()
        except IntegrityError as e:
            sess.rollback()
            raise e
        return inst

    @classmethod
    def review(kls, **kwargs):
        sess = session()
        inst = kls.query.filter_by(**kwargs).first()
        return inst

    @classmethod
    def update(kls, **kwargs):
        sess = session()
        inst = kls.query.filter_by(id=kwargs['id']).first()
        for k, v in kwargs.items():
            setattr(inst, k, v)
        sess.add(inst)
        try:
            sess.commit()
        except IntegrityError as e:
            sess.rollback()
            raise e
        return inst

    @classmethod
    def delete(kls, **kwargs):
        sess = session()
        inst = kls.query.filter_by(**kwargs).first()
        try:
            sess.delete(inst)
            sess.commit()
        except (AttributeError, UnmappedInstanceError) as e:
            sess.rollback()
            raise e


class Model(ModelBase, Base):

    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def as_json(self):
        d = {
            'id': str(self.id),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        return d