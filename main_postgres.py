import psycopg2
import postgres_queries_operator as postgres_qo
import data_generator as postgres_dg
from data_instances_count_cap import cap_dic
import time

tables_rows_count_cap = cap_dic
DATABASE_CONFIG = {
    "dbname": "ZTBD2",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,  # default PostgreSQL port
}

def insert_operation(data_generator, multiplier=1):
    for table_name in tables_rows_count_cap.keys():
        for i in range((tables_rows_count_cap[table_name] * multiplier) - data_generator.tables_records_count[table_name]):
            record = data_generator.records_generators[table_name]()
            queries_operator.insert_into_table(cursor, table_name, record)
            conn.commit()

        data_generator.tables_records_count[table_name] = (
            queries_operator.get_table_rows_count(cursor, table_name)[0]
        )

try:
    # Połączenie z bazą danych
    queries_operator = postgres_qo.QueriesOperator()
    conn = psycopg2.connect(**DATABASE_CONFIG)

    # Tworzenie kursora do wykonywania zapytań
    cursor = conn.cursor()

    # Przykładowe zapytanie
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print("Wersja PostgreSQL:", db_version)
    
    data_generator = postgres_dg.DataGenerator()

    multipliers = [1, 10, 100, 1000, 3000]
    for multiplier in multipliers:
        print("multiplier: ", multiplier)
        # initialization of tables, if they don't exist
        queries_operator.create_tables(cursor, conn)
        for key in data_generator.tables_records_count.keys():
            data_generator.tables_records_count[key] = queries_operator.get_table_rows_count(cursor, key)[0]
        print(data_generator.tables_records_count)

        # insert operation test:
        start = time.time()
        insert_operation(data_generator, multiplier)
        end = time.time()
        print("insert time elapsed: ", end-start)
        print(data_generator.tables_records_count)

        start = time.time()
        queries_operator.select_1(cursor)
        end = time.time()
        select_result = cursor.fetchmany(3)
        print("query: ", queries_operator.select_from_pogoda)
        print("select time elapsed: " ,end-start,"results count: ", cursor.rowcount, " first three:")
        print(select_result, "\n")

        start = time.time()
        queries_operator.select_2(cursor)
        end = time.time()
        select_result = cursor.fetchmany(3)
        print("query: ", queries_operator.select_inner_join)
        print("select time elapsed: " ,end-start,"results count: ", cursor.rowcount, " first three:")
        print(select_result, "\n")

        start = time.time()
        queries_operator.update_1(cursor, conn)
        end = time.time()
        #result = cursor.fetchmany(3)
        print("query: ", queries_operator.update_query)
        print("update time elapsed: " ,end-start,"results count: ", cursor.rowcount, "\n")
        #print(result, "\n")

        #deleting all records:
        start = time.time()
        queries_operator.delete_all_records_from_tables(cursor, conn)
        end = time.time()
        print("delete time elapsed: ", end-start)

        queries_operator.drop_tables(cursor, conn)
        print("dropped tables\n")

    conn.commit()

    # Zamykanie kursora i połączenia
    cursor.close()
    conn.close()

except psycopg2.Error as e:
    print("Error connecting to the database:", e)
