import random
from datetime import datetime, timedelta
from psycopg2.extensions import adapt, AsIs

class DataGenerator:

    def __init__(self, for_mongo=False):
        self.for_mongo = for_mongo

        self.tables_records_count = {
            "historia": 0,
            "obiekt_geograficzny": 0,
            "sektor": 0,
            "pogoda": 0,
        }

        self.records_generators = {
            "sektor": self.generate_sektor_record,
            "historia": self.generate_historia_record,
            "obiekt_geograficzny": self.generate_obiekt_geograficzny_record,
            "pogoda": self.generate_pogoda_record,
        }

        self.start_date = datetime(2025, 1, 1)
        self.end_date = datetime(2025, 1, 7)
        self.lake_north_bound_radians = 0.945037
        self.lake_south_bound_radians = 0.943005
        self.lake_west_bound_radians = 0.376568
        self.lake_east_bound_radians = 0.380010

    def adapt_point(self, x, y):
        x = adapt(x).getquoted()
        y = adapt(y).getquoted()

        return AsIs("'(%s, %s)'" % (x.decode("utf-8"), y.decode("utf-8")))
    
    def get_point(self):
        x = random.uniform(self.lake_west_bound_radians, self.lake_east_bound_radians)
        y = random.uniform(self.lake_south_bound_radians, self.lake_north_bound_radians)
        
        if self.for_mongo:
            return (x, y)
        else:
            return self.adapt_point(x, y)

    # ( ( x1 , y1 ) , ... , ( xn , yn ) )
    def get_polygon(self, vertices_count=3):
        polygon_string = "("

        for i in range(vertices_count):
            x = random.uniform(
                self.lake_west_bound_radians, self.lake_east_bound_radians
            )
            y = random.uniform(
                self.lake_south_bound_radians, self.lake_north_bound_radians
            )
            polygon_string += f"({x},{y}),"

        polygon_string = polygon_string[:-1]  # Remove the trailing comma
        polygon_string += ")"
        polygon_string = adapt(polygon_string).getquoted().decode("utf-8")

        if self.for_mongo:
            return polygon_string
        else:
            return AsIs(f"{polygon_string}")

    def generate_random_datetime(self):
        delta = self.end_date - self.start_date
        random_seconds = random.randint(
            0, int(delta.total_seconds())
        )  # Random seconds in range

        return self.start_date + timedelta(seconds=random_seconds)

    def generate_historia_record(self):
        date_val = self.generate_random_datetime()

        geo_position = self.get_point()

        vessel_direction = random.uniform(0, 359)
        speed = random.uniform(-3, 15)
        fk_sektor = random.randint(
            1, self.tables_records_count["sektor"]
        ) 
  
        return {
            "czas_pomiaru": date_val,
            "fk_sektor": fk_sektor,
            "koordynaty_punkt": geo_position,
            "zwrot_statku": vessel_direction,
            "predkosc": speed,
        }

    def generate_obiekt_geograficzny_record(self):
        object_types = [
            "boja",
            "latarnia",
            "znak wodny",
            "trzęsawisko",
            "mina morska",
            "wrak",
        ]

        geo_position = self.get_point()

        object_type = random.choice(object_types)
        radius = random.uniform(1, 50)
        fk_sektor = random.randint(
            1, self.tables_records_count["sektor"]
        )

        return {
            "fk_sektor": fk_sektor,
            "koordynaty_punkt": geo_position,
            "typ_obiektu": object_type,
            "promien": radius,
        }

    def generate_sektor_record(self):
        coordinates = self.get_polygon(4)

        return {"koordynaty": coordinates}

    def generate_pogoda_record(self):
        weather_types = [
            "tęcza",
            "bezchmurnie",
            "częściowe zachmurzenie",
            "całkowite zachmurzenie",
            "deszcz",
            "sztorm",
        ]

        fk_sektor = random.randint(
            1, self.tables_records_count["sektor"]
        )
        date_val = self.generate_random_datetime()
        weather_type = random.choice(weather_types)
        beaufort_scale_val = random.randint(
            0, 9
        )  # https://pl.wikipedia.org/wiki/Skala_Beauforta
        wind_direction = random.uniform(0, 359)

        return {
            "fk_sektor": fk_sektor,
            "czas_pomiaru": date_val,
            "typ_pogody": weather_type,
            "skala_Beauforta": beaufort_scale_val,
            "kierunek_wiatru": wind_direction,
        }