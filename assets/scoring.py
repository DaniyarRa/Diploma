import pandas as pd
import math
from sqlalchemy import create_engine, Column, String, Integer, Date, Float, TIMESTAMP, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()

class CrimeRecord(Base):
    __tablename__ = 'crime'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    date_excitation = Column(Date)
    crime_title = Column(String(256), nullable=False)
    crime_level = Column(Integer)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)

class AreaScoringRecord(Base):
    __tablename__ = 'area_scoring'
    __table_args__ = {'schema': 'mart'}

    id = Column(Integer, primary_key=True)
    step_id = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('step_id', 'latitude', 'longitude'),
        {'schema': 'mart'}
    )

class AreaPopulationRecord(Base):
    __tablename__ = 'area_population'
    __table_args__ = {'schema': 'mart'}

    id = Column(Integer, primary_key=True)
    step_id = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    age0_15 = Column(Integer)
    age16_25 = Column(Integer)
    age26_35 = Column(Integer)
    age36_45 = Column(Integer)
    age46_55 = Column(Integer)
    age56_65 = Column(Integer)
    age66_100 = Column(Integer)
    total = Column(Integer)
    density = Column(Float)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('step_id', 'latitude', 'longitude'),
        {'schema': 'mart'}
    )


def get_actual_crimininal_data(step_id, step, session):
    source_data = session.query(CrimeRecord).all()
    population_data = session.query(AreaPopulationRecord).filter(AreaPopulationRecord.step_id == step_id).all()

    df = pd.DataFrame([{
        'date': item.date,
        'date_excitation': item.date_excitation,
        'crime_title': item.crime_title,
        'crime_level': item.crime_level,
        'latitude': item.latitude,
        'longitude': item.longitude
    } for item in source_data])

    df2 = pd.DataFrame([{
        'latitude': item.latitude,
        'longitude': item.longitude,
        'density': item.density
    } for item in population_data])

    mean_density = df2['density'].mean()
    df2['density'].replace(0, mean_density, inplace=True)

    df['date'] = pd.to_datetime(df['date'])

    months_diff = (df['date'].max().year - df['date'].min().year) * 12 + (df['date'].max().month - df['date'].min().month) + 1

    step_len = len(str(step).split('.')[1])
    df['latitude'] = df['latitude'].apply(lambda x: round((math.floor(x * (1 / step)) * step) + float(step), step_len))
    df['longitude'] = df['longitude'].apply(lambda x: round(math.floor(x * (1 / step)) * step, step_len))

    common_y_values = df.groupby('crime_title')['crime_level'].agg(lambda x: x.mode().iloc[0])

    df['crime_level'] = df.apply(lambda row: common_y_values[row['crime_title']] if row['crime_level'] == 0 else row['crime_level'], axis=1)
    df['score'] = df['crime_level']

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    df = (df[['latitude', 'longitude', 'year', 'month', 'score']].groupby(by=['latitude', 'longitude', 'year', 'month'])
          .mean('score').reset_index())

    df = (df[['latitude', 'longitude', 'score']].groupby(by=['latitude', 'longitude'])
          .sum('score').reset_index())

    df = pd.merge(df, df2, on=['latitude', 'longitude'], how='left')
    df['density'] = df['density'].fillna(mean_density)

    df['score'] = df['score'] / (months_diff * df['density'] * step * step)
    df['step_id'] = step_id

    df = df.drop('density', axis=1)

    df_dict = df.to_dict(orient='records')
    for row in df_dict:
        new_record = AreaScoringRecord(**row)
        session.add(new_record)

    return

def init():
    database_url = "postgresql://postgres:%211Qwerty1974%402@35.205.69.113:5432/diploma-db"

    engine = create_engine(database_url)
    AreaScoringRecord.__table__.drop(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    get_actual_crimininal_data(1, 0.0025, session)
    get_actual_crimininal_data(2, 0.005, session)
    get_actual_crimininal_data(3, 0.01, session)

    session.commit()
    session.close()

init()

