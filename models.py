import mysql.connector
from mysql.connector import Error

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='smart_kitchen_db'
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def init_db():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ingredient VARCHAR(255) NOT NULL,
            quantity INT NOT NULL
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()

def add_ingredient(ingredient, quantity):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO inventory (ingredient, quantity) VALUES (%s, %s)', (ingredient, quantity))
    connection.commit()
    cursor.close()
    connection.close()

def get_inventory():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM inventory')
    items = cursor.fetchall()
    cursor.close()
    connection.close()
    return items