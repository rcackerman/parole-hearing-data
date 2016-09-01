from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from .base import Model


class Person(Model):

    __tablename__ = 'people'

    din = Column(String, nullable=False)
    birth_date = Column(Date)
    sex = Column(String)
    race_ethnicity = Column(String)



class ParoleBoardInterviews(Model):

    __tablename__ = 'parole_board_interviews'

    person_id = Column(Integer, ForeignKey('people.id'), nullable=False, index=True)
    date = Column(Date)
    type = Column(String)
    facility = Column(String)
    decision = Column(String, nullable=True)
