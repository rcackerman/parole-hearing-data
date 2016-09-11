from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from .base import Model


class Person(Model):

    __tablename__ = 'people'

    nysid = Column(String)
    birth_date = Column(Date)
    sex = Column(String)
    race_ethnicity = Column(String)


class Parolee(Model):

    __tablename__ = 'parolees'

    person_id = Column(Integer, ForeignKey('people.id'), nullable=False, index=True)
    din = Column(String, nullable=False)
    year_of_entry = Column(Integer)
    aggregated_minimum_sentence = Column(String)
    aggregated_maximum_sentence = Column(String)
    housing_or_release_facility = Column(String)
    housing_or_release_facility_security = Column(String)
    conditional_release_date = Column(Date)
    parole_eligibility_date = Column(Date)
    maximum_expiration_date = Column(Date)
    parole_maximum_expiration_date = Column(Date)
    post_release_supervision_me_date = Column(Date)
    parole_board_discharge_date = Column(Date)


class Crimes(Model):

    __tablename__ = 'crimes'

    parolee_id = Column(Integer, ForeignKey('parolees.id'), nullable=False, index=True)
    crime_of_conviction = Column(String)
    county_of_commitment = Column(String)
    class_of_crime = Column(String)


class ParoleBoardInterviews(Model):

    __tablename__ = 'parole_board_interviews'

    parolee_id = Column(Integer, ForeignKey('parolees.id'), nullable=False, index=True)
    interview_date = Column(Date)
    interview_type = Column(String)
    interview_decision = Column(String)
    interview_decision_category = Column(string)
    housing_or_interview_facility = Column(String)
    release_date = Column(Date)
    release_type = Column(String)
