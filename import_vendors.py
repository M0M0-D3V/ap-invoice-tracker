import csv

import mysql.connector

from db import get_connection

inserted = 0
duplicates = 0
invalid = 0

conn = get_connection()
cursor = conn.cursor()

with open("vendors.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["vendor_name"].strip()
        if not name:
            invalid += 1
            continue
        try:
            cursor.execute(
                "INSERT INTO vendors (vendor_name) VALUES (%s)",
                (name,),
            )
            conn.commit()
            inserted += 1
        except mysql.connector.IntegrityError:
            duplicates += 1
            print(f"Duplicate skipped: {name}")

cursor.close()
conn.close()

print(f"Inserted: {inserted}, Duplicates: {duplicates}, Invalid: {invalid}")