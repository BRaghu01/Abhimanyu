import create_connection as cc
from mysql.connector import Error
from datetime import date

def get_ingredients():
    connection = cc.create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM Inventory")
            ingredients = cursor.fetchall()
            for ingredient in ingredients:
                print(ingredient)
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

# Get list of ingredients
get_ingredients()