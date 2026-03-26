from psycopg2 import sql


class QueriesOperator:

    def __init__(self):
        self.tables_creation_queries = {
            "obiekt_geograficzny": "CREATE TABLE IF NOT EXISTS obiekt_geograficzny (p_key SERIAL PRIMARY KEY, fk_sektor INT references sektor(p_key), koordynaty_punkt POINT, typ_obiektu VARCHAR(128), promien INT);",
            "historia": "CREATE TABLE IF NOT EXISTS historia (p_key serial PRIMARY KEY, fk_sektor INT references sektor(p_key), czas_pomiaru TIMESTAMP, koordynaty_punkt POINT, zwrot_statku INT, predkosc REAL);",
            "pogoda": "CREATE TABLE IF NOT EXISTS pogoda (p_key serial PRIMARY KEY, fk_sektor INT references sektor(p_key), czas_pomiaru TIMESTAMP, typ_pogody VARCHAR(128), skala_Beauforta INT, kierunek_wiatru INT);",
            "sektor": "CREATE TABLE IF NOT EXISTS sektor (p_key serial PRIMARY KEY, koordynaty POLYGON);",
        }

        self.tables_insert_queries = {
            "obiekt_geograficzny": "INSERT INTO obiekt_geograficzny (fk_sektor, koordynaty_punkt, typ_obiektu, promien) VALUES (%(fk_sektor)s, %(koordynaty_punkt)s, %(typ_obiektu)s, %(promien)s);",
            "historia": "INSERT INTO historia (fk_sektor, czas_pomiaru, koordynaty_punkt, zwrot_statku, predkosc) VALUES (%(fk_sektor)s, %(czas_pomiaru)s, %(koordynaty_punkt)s, %(zwrot_statku)s, %(predkosc)s);",
            "pogoda": "INSERT INTO pogoda (fk_sektor, czas_pomiaru, typ_pogody, skala_Beauforta, kierunek_wiatru) VALUES (%(fk_sektor)s, %(czas_pomiaru)s, %(typ_pogody)s, %(skala_Beauforta)s, %(kierunek_wiatru)s);",
            "sektor": "INSERT INTO sektor (koordynaty) VALUES (%(koordynaty)s);",
        }

        self.get_table_rows_count_query = "SELECT count(*) from {table_name};"
        self.delete_all_table_rows_query = "DELETE FROM {table_name};"
        self.drop_table_query = "DROP TABLE {table_name} CASCADE;"
        self.select_from_pogoda = "SELECT czas_pomiaru FROM pogoda WHERE skala_beauforta>3 ORDER BY skala_beauforta DESC;"

        self.select_inner_join = "SELECT pogoda.typ_pogody, pogoda.czas_pomiaru, obiekt_geograficzny.typ_obiektu FROM obiekt_geograficzny INNER JOIN pogoda ON pogoda.fk_sektor=obiekt_geograficzny.fk_sektor"
        self.select_inner_join_2 = "SELECT pogoda.typ_pogody, pogoda.czas_pomiaru, obiekt_geograficzny.typ_obiektu FROM obiekt_geograficzny INNER JOIN pogoda ON pogoda.fk_sektor=obiekt_geograficzny.fk_sektor WHERE obiekt.geograficzny.fk_sektor BETWEEN %(lower_bound)s AND %(upper_bound)s"

        self.update_query = "UPDATE obiekt_geograficzny SET promien=3 WHERE typ_obiektu='latarnia'"

    def update_1(self, cursor, conn):
        cursor.execute(self.update_query)

    def select_2(self, cursor):
        cursor.execute(self.select_inner_join)

    def select_1(self, cursor):
        cursor.execute(self.select_from_pogoda)

    def delete_all_records_from_tables(self, cursor, conn):
        cursor.execute(sql.SQL(self.delete_all_table_rows_query).format(table_name=sql.Identifier("pogoda")))
        cursor.execute(sql.SQL(self.delete_all_table_rows_query).format(table_name=sql.Identifier("historia")))
        cursor.execute(sql.SQL(self.delete_all_table_rows_query).format(table_name=sql.Identifier("obiekt_geograficzny")))
        cursor.execute(sql.SQL(self.delete_all_table_rows_query).format(table_name=sql.Identifier("sektor")))

        conn.commit()

    def drop_tables(self, cursor, conn):
        cursor.execute(sql.SQL(self.drop_table_query).format(table_name=sql.Identifier("sektor")))
        cursor.execute(sql.SQL(self.drop_table_query).format(table_name=sql.Identifier("pogoda")))
        cursor.execute(sql.SQL(self.drop_table_query).format(table_name=sql.Identifier("historia")))
        cursor.execute(sql.SQL(self.drop_table_query).format(table_name=sql.Identifier("obiekt_geograficzny")))

        conn.commit()


    def create_tables(self, cursor, conn):
        cursor.execute(self.tables_creation_queries["sektor"])
        conn.commit()

        cursor.execute(self.tables_creation_queries["pogoda"])
        cursor.execute(self.tables_creation_queries["historia"])
        cursor.execute(self.tables_creation_queries["obiekt_geograficzny"])
        conn.commit()

    def insert_into_table(self, cursor, table_name, data_list):
        cursor.execute(self.tables_insert_queries[table_name], data_list)

    def get_table_rows_count(self, cursor, table_name):
        cursor.execute(
            sql.SQL(self.get_table_rows_count_query).format(
                table_name=sql.Identifier(table_name)
            )
        )
        results = cursor.fetchone()

        return results
