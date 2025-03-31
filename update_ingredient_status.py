import create_connection as cc
from mysql.connector import Error
from datetime import date

# Update Ingredient Status (e.g., marking an ingredient as spoiled)
def update_ingredient_status(ingredient_name, new_status):
    connection = cc.create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE Inventory
                SET status = %s
                WHERE ingredient_name = %s
            """, (new_status, ingredient_name))
            print(f"Ingredient {ingredient_name} status updated to {new_status}")
            connection.commit()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

# Update ingredient status (e.g., marking it as spoiled)    
update_ingredient_status("Tomato", "spoiled")