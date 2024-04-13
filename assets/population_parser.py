import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import json
from sqlalchemy import create_engine, Column, String, Integer, Float, TIMESTAMP, func, select
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.schema import UniqueConstraint
from shapely.geometry import Polygon
from pyproj import Proj, transform
import requests

Base = declarative_base()
utm_zone_43N = Proj(init='epsg:32643')
wgs84 = Proj(init='epsg:4326')

area_s = [0.05638528, 0.225545684, 0.902219241]
step = [0.0025, 0.005, 0.01]
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

def save_to_database(data, session):
    record = AreaPopulationRecord(
        step_id=data['step_id'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        age0_15=data['all_ages'][0],
        age16_25=data['all_ages'][1],
        age26_35=data['all_ages'][2],
        age36_45=data['all_ages'][3],
        age46_55=data['all_ages'][4],
        age56_65=data['all_ages'][5],
        age66_100=data['all_ages'][6],
        total=data['total'],
        density=data['density']
    )

    session.add(record)
    session.commit()

    print('New population info: ', data['step_id'], '-', data['longitude'], '-', data['latitude'], sep='')

def fetch_and_parse_json(url):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()  # Check for any HTTP errors

        data = response.json()  # Parse JSON data from the response
        return data
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def main():
    database_url = "postgresql://postgres:%211Qwerty1974%402@35.205.69.113:5432/diploma-db"
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for i in session.execute(select(AreaScoringRecord.step_id, AreaScoringRecord.latitude, AreaScoringRecord.longitude)).all():

        step_id = i[0]
        latitude = i[1]
        longitude = i[2]
        poly = [(longitude, latitude), (round(longitude + step[step_id - 1], 4), latitude), (round(longitude + step[step_id - 1], 4), latitude - step[step_id - 1]), (longitude, latitude - step[step_id - 1])]

        poly_converted = [tuple(transform(wgs84, utm_zone_43N, pair[0], pair[1])) for pair in poly]

        url = f'https://mapalmaty.kz/arcgis/rest/services/d302_demo_test/MapServer/identify?f=json&tolerance=0&returnGeometry=true&returnFieldName=false&returnUnformattedValues=false&imageDisplay=884%2C687%2C96&geometry=%7B%22xmin%22%3A{poly_converted[0][0]}%2C%22ymin%22%3A{poly_converted[2][1]}%2C%22xmax%22%3A{poly_converted[2][0]}%2C%22ymax%22%3A{poly_converted[0][1]}%7D&geometryType=esriGeometryEnvelope&sr=32643&mapExtent=647934.2189728817%2C4790437.015588599%2C652285.7388384432%2C4793818.7962986&layers=all%3A0'

        data = fetch_and_parse_json(url)

        d = {'step_id': step_id, 'latitude': latitude, 'longitude': longitude, 'all_ages': [0, 0, 0, 0, 0, 0, 0], 'total': 0, 'density': 0}
        data = data.get('results') or []
        for area in data:
            area_poly = area['geometry']['rings'][0]
            area_poly = [tuple(transform(utm_zone_43N, wgs84, pair[0], pair[1])) for pair in area_poly]

            poly = Polygon(poly)
            area_poly = Polygon(area_poly)

            intersection = poly.intersection(area_poly)

            percentage = (intersection.area / area_poly.area)

            ages = area['attributes']['COUNT']

            if ages == 'NULL':
                continue

            ages = [round(int(age) * percentage) for age in area['attributes']['COUNT'].split(';')]
            d['all_ages'] = [x + y for x, y in zip(d['all_ages'], ages)]

        d['total'] = sum(d['all_ages'])
        d['density'] = d['total'] / area_s[d['step_id'] - 1]

        save_to_database(d, session)

    session.close()


if __name__ == "__main__":
    main()
