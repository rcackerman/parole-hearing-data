from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
Base.query = db_session.query_property()


class Crime(Base):
	__tablename__ = 'crimes'

	id = Column(Integer, primary_key = True)
	name = Column(String)
	crime_class = Column(String)
	county = Column(String)

class Sentence(Base):
	__tablename__ = 'sentences'

	id = Column(Integer, primary_key = True)
	name = Column(String)


class Inmate(Base):
	__tablename__ = 'inmates'

	id = Column(Integer, primary_key = True)
	last_name = Column(String)
	first_name = Column(String)
	nysid = Column(BigInteger)
	din = Column(BigInteger)
	sex = Column(String)
	birth_date = Column(Date)
	race = Column(String)
	entry_year = Column(Integer)
	release_date = Column(Date)
	conditional_release_date = Column(Date)
	parole_discharge_date = Column(Date)

	crime_id = Column(Integer, ForeignKey('crimes.id'))
	sentence_id = Column(Integer, ForeignKey('sentences.id'))
	parole_id = Column(Integer, ForeignKey('hearings.id'))
	housing_interview_facility_id = Column(Integer, ForeignKey('facilities.id'))


class Facility(Base):
	__tablename__ = 'facilities'
	name = Column(String)
	county = Column(String)

class Hearing(Base):
	__tablename__ = 'hearings'

	id = Column(Integer, primary_key = True)
	interview_date = Column(Date)
	interview_type = Column(String)
	interview_decision = Column(String)