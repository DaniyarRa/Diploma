import json
from sqlalchemy import create_engine, Column, String, Integer, Float, TIMESTAMP, func, select
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class CityObject(Base):
    __tablename__ = 'city_object'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True)
    object_type = Column(String(256))
    name = Column(String(256), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)


def save_to_database(data, session):
    l = [i[:3] for i in session.execute(select(CityObject.name, CityObject.latitude, CityObject.longitude)).all()]

    for obj in data:
        if (obj["name"], float(obj["lat"]), float(obj["lon"])) not in l:
            record = CityObject(
                object_type='transport',
                name=obj["name"],
                latitude=float(obj["lat"]),
                longitude=float(obj["lon"])
            )

            session.add(record)
            session.commit()

            print('New object info:', obj['name'])

    print("Data saved to database successfully.")


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def main():
    json_file_path = 'payload.json'
    data = read_json_file(json_file_path)

    database_url = "postgresql://postgres:%211Qwerty1974%402@35.205.69.113:5432/diploma-db"
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    data = data['result'].get('items') or []
    save_to_database(data, session)

    session.close()


if __name__ == "__main__":
    main()
