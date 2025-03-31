import create_connection as cc
from mysql.connector import Error
from datetime import date

# Delete Expired Ingredients
def delete_expired_ingredients():
    connection = cc.create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Deleting expired ingredients
            cursor.execute("DELETE FROM Inventory WHERE expiry_date < %s AND status != 'spoiled'", (date.today(),))
            print("Expired ingredients deleted successfully")
            connection.commit()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

# Delete expired ingredients
delete_expired_ingredients()