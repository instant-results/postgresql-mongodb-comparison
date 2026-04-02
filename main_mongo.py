# hello world
import pymongo
import random
from datetime import datetime, timedelta
import data_generator as postgres_dg
from data_instances_count_cap import cap_dic
import time

collection_dictionaries_count_cap = cap_dic


def insert_operation(data_generator, multiplier=1):
    for coll_name, coll_documents_count_cap in collection_dictionaries_count_cap.items():
        collection = getattr(db, coll_name)

        for i in range((coll_documents_count_cap * multiplier) - data_generator.tables_records_count[coll_name]):
            record = data_generator.records_generators[coll_name]()
            x = collection.insert_one(record)

        data_generator.tables_records_count[coll_name] = collection.count_documents({})

def delete_all_documents_from_collections():
    db.sektor.delete_many({})
    db.pogoda.delete_many({})
    db.historia.delete_many({})
    db.obiekt_geograficzny.delete_many({})

def find_from_pogoda():
    results = db.pogoda.find(
    {"skala_Beauforta": {"$gt": 3}},  # Warunek WHERE: skala_Beauforta > 3
    {"czas_pomiaru": 1, "_id": 0}     # Wybór kolumn: czas_pomiaru
).sort("skala_Beauforta", -1)         # Sortowanie: DESC według skala_Beauforta

    return results

def aggregation_query():
    # Agregacja
    pipeline = [
        {
            "$lookup": {
                "from": "pogoda",          # Kolekcja, z którą wykonujemy JOIN
                "localField": "fk_sektor", # Pole z obiekt_geograficzny
                "foreignField": "fk_sektor", # Pole z pogoda
                "as": "pogoda_data"        # Nazwa nowego pola
            }
        },
        {
            "$unwind": "$pogoda_data" 
        },
        {
            "$project": {                   
                "typ_pogody": "$pogoda_data.typ_pogody",
                "typ_obiektu": "$typ_obiektu"
            }
        }
    ]

    results = db.obiekt_geograficzny.aggregate(pipeline)

    return results

def update_query():
    result = db.obiekt_geograficzny.update_many(
        {"typ_obiektu": "latarnia"},
        {"$set": {"promien": 3}}
    )

    return result


try:
    print("connecting to Mongo")
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client.ZTBD
    print(client.list_database_names())

    data_generator = postgres_dg.DataGenerator(for_mongo=True)

    multipliers = [1, 10, 100, 1000, 3000]
    for multiplier in multipliers:
        print("mongdodb multiplier: ", multiplier)

        for key in data_generator.tables_records_count.keys():
            collection = getattr(db, key)
            documents_count = collection.count_documents({})
            data_generator.tables_records_count[key] = documents_count
        print(data_generator.tables_records_count)

        start = time.time()
        insert_operation(data_generator, multiplier)
        end = time.time()
        print("insert time elapsed: ", end-start)
        print(data_generator.tables_records_count, "\n")

        start = time.time()
        results = find_from_pogoda()
        end = time.time()
        print("find from pogoda time elapsed: ", end-start)
        print("first 3 documents:")
        for document in results.to_list(3):
            print(document)
        print()

        start = time.time()
        results = aggregation_query()
        end = time.time()
        print("aggregation query time: ", end-start)
        print("first 3 documents:")
        for document in results.to_list(3):
            print(document)
        print()

        start = time.time()
        result = update_query()
        end = time.time()
        print("update query time: ", end-start)
        print("affected documents count:")
        print(result)
        print(result.modified_count, "\n")

        start = time.time()
        delete_all_documents_from_collections()
        end = time.time()
        print("delete time elapsed: ", end-start)
        print()
    
except pymongo.errors.ConnectionFailure as e:
    print("Error connecting to the database:", e)    
