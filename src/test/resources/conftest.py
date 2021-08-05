import os

import mysql.connector
import pytest
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="module")
def mysql_cursor():
    mydb = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        autocommit=True
    )
    mycursor = mydb.cursor()
    yield mycursor
    mycursor.close()
    mydb.close()

@pytest.fixture(scope="module")
def temp_id_number(mysql_cursor):
    mycursor = mysql_cursor
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = ("Other", "test0", -36.972951428258774, -54.477748758095, "https://www.test.com/0")
    mycursor.execute(insert, val)
    id_number = mycursor.lastrowid
    yield id_number
    mycursor.execute(f"DELETE FROM problems WHERE id = {id_number}")