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

def get_actual_crimininal_data(step_id, step, session):
    source_data = session.query(CrimeRecord).all()

    df = pd.DataFrame([{
        'date': item.date,
        'date_excitation': item.date_excitation,
        'crime_title': item.crime_title,
        'crime_level': item.crime_level,
        'latitude': item.latitude,
        'longitude': item.longitude
    } for item in source_data])

    step_len = len(str(step).split('.')[1])
    df['latitude'] = df['latitude'].apply(lambda x: round((math.floor(x * (1 / step)) * step) + float(step), step_len))
    df['longitude'] = df['longitude'].apply(lambda x: round(math.floor(x * (1 / step)) * step, step_len))

    common_y_values = df.groupby('crime_title')['crime_level'].agg(lambda x: x.mode().iloc[0])

    df['crime_level'] = df.apply(lambda row: common_y_values[row['crime_title']] if row['crime_level'] == 0 else row['crime_level'], axis=1)

    df['date'] = pd.to_datetime(df['date'])

    current_month = pd.Timestamp.now().month

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    df['slope'] = (df['year'] - pd.Timestamp.now().year) * 12 + df['month'] - current_month + 100
    df['slope'] = df['slope'].apply(lambda x: 0 if x < 0 else x)
    df['score'] = df['crime_level'] * df['slope']

    df = (df[['latitude', 'longitude', 'year', 'month', 'score']].groupby(by=['latitude', 'longitude', 'year', 'month'])
          .sum('score').reset_index())

    df = (df[['latitude', 'longitude', 'score']].groupby(by=['latitude', 'longitude'])
          .mean('score').reset_index())

    df['score'] = df['score'] / (step * step * 10000)
    df['step_id'] = step_id
    df_dict = df.to_dict(orient='records')
    for row in df_dict:
        new_record = AreaScoringRecord(**row)
        session.add(new_record)

    data = df.set_index(['latitude', 'longitude'])['score'].to_dict()
    #print('data_in_scoring:', data)

    return data

def init(step):
    database_url = "postgresql://postgres:%211Qwerty1974%402@35.205.69.113:5432/diploma-db"

    engine = create_engine(database_url)
    AreaScoringRecord.__table__.drop(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    step_1_data = get_actual_crimininal_data(1, 0.0025, session)
    step_2_data = get_actual_crimininal_data(2, 0.005, session)
    step_3_data = get_actual_crimininal_data(3, 0.01, session)

    session.commit()
    session.close()

    if step == 0.0025:
        return step_1_data
    elif step == 0.005:
        return step_2_data
    else:
        return step_3_data
