import create_connection as cc
from mysql.connector import Error
from datetime import date

# Add Ingredient
def add_ingredient(ingredient_name, quantity, expiry_date, image_url):
    connection = cc.create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Calculate the difference in days between today and expiry date
            today = date.today()
            expiry_date_obj = date.fromisoformat(expiry_date)
            difference = (expiry_date_obj - today).days
            
            # Determine the status based on the difference
            if difference <= 2:
                status = "near expiry"
            elif 2 < difference <= 3:
                status = "useful"
            else:
                status = "fresh"
            
            # Inserting new ingredient into Inventory
            cursor.execute("""
                INSERT INTO Inventory (ingredient_name, quantity, expiry_date, image_url, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (ingredient_name, quantity, expiry_date, image_url, status))
            print("Ingredient added successfully")
            connection.commit()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

# Example usage
add_ingredient("Mango", 35, "2025-04-10", "updated_url_to_image")