import requests
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Integer, Date, Float, TIMESTAMP, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

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


def fetch_and_parse_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for any HTTP errors

        data = response.json()  # Parse JSON data from the response
        return data
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def save_to_database(data, from_date, session):
    if not data:
        print("No data to save.")
        return
    print('data before db:', data)
    for crime in data:
        record = CrimeRecord(
            date=datetime.strptime(from_date, "%d.%m.%Y").date(),
            date_excitation=datetime.strptime(crime["date_excitation"], "%d.%m.%Y").date() if crime[
                "date_excitation"] else None,
            crime_title=crime["crime_title"],
            crime_level=crime["hard_code"],
            latitude=float(crime["location"]["lat"]),
            longitude=float(crime["location"]["lon"])
        )
        session.add(record)

    session.commit()
    print("Data saved to database successfully.")


def main(start_date, end_date, database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    base_url = "https://krisha.kz/ms/geodata/crime"
    params = {
        "bounds": "76.65060394531248,43.4253116907793,77.12026947265623,43.11019905275058",
        "limit": "500",
        "fields": "crime_title,hard_code,date_excitation"
    }

    start = datetime.strptime(start_date, "%d.%m.%Y")
    end = datetime.strptime(end_date, "%d.%m.%Y")
    delta = timedelta(days=1)

    while start <= end:
        from_date = start.strftime("%d.%m.%Y")
        params["from"] = from_date
        params["to"] = start.strftime("%d.%m.%Y")
        url = f"{base_url}?{requests.compat.urlencode(params)}"

        crime_data = fetch_and_parse_json(url)
        save_to_database(crime_data, from_date, session)

        start += delta

    session.close()


def init():
    date = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
    database_url = "postgresql://postgres:%211Qwerty1974%402@35.205.69.113:5432/diploma-db"
    main(date, date, database_url)


init()
