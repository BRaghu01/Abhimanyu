import create_connection as cc
import pandas as pd
import mysql.connector
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from datetime import datetime

def fetch_data_from_db():
    """Fetch data from smart_kitchen database with validation"""
    try:
        conn = cc.get_connection()
        if not conn:
            print("Database connection failed")
            return None

        cursor = conn.cursor()

        cursor.execute("SHOW DATABASES LIKE 'smart_kitchen'")
        if not cursor.fetchone():
            print("Error: Database 'smart_kitchen' not found")
            return None

        cursor.execute("SHOW TABLES")
        existing_tables = {table[0] for table in cursor.fetchall()}
        required_tables = {'sales', 'inventory', 'waste', 'demandforecast', 'ingredients'}
        
        missing_tables = required_tables - existing_tables
        if missing_tables:
            print(f"Missing tables: {', '.join(missing_tables)}")
            return None

        data = {}
        for table in required_tables:
            cursor.execute(f"SELECT * FROM {table}")
            data[table] = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
        
        return (data['sales'], data['inventory'], data['waste'], data['demandforecast'], data['ingredients'])

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

def preprocess_data(sales, inventory, waste, demand_forecast, ingredients):
    """Preprocess and merge data from multiple tables"""
    inventory_merged = pd.merge(inventory, ingredients, on='ingredient_id', suffixes=('_inv', '_ing'))

    today = datetime.now().date()
    sales['sale_date'] = pd.to_datetime(sales['sale_date'])
    inventory_merged['expiry_date'] = pd.to_datetime(inventory_merged['expiry_date_inv'])

    daily_sales = sales.groupby(['ingredient_id', 'sale_date'], as_index=False)['quantity_sold'].sum()

    merged = pd.merge(inventory_merged, waste, on='ingredient_id', how='left')
    merged = pd.merge(merged, demand_forecast, on='ingredient_id', how='left')

    merged['days_until_expiry'] = (merged['expiry_date'] - pd.to_datetime(today)).dt.days
    merged['quantity_wasted'] = merged['quantity_wasted'].fillna(0)
    merged['reason'] = merged['reason'].fillna('No Waste')

    return merged, daily_sales

def demand_forecasting(ingredient_id, sales_data):
    """Time-series forecasting using Prophet"""
    if sales_data.empty or len(sales_data) < 5:  # Ensure enough data
        return None
        
    try:
        df = sales_data.rename(columns={'sale_date': 'ds', 'quantity_sold': 'y'})
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=7)
        forecast = model.predict(future)
        return forecast['yhat'].iloc[-1]
    except Exception as e:
        print(f"Forecast error for ingredient {ingredient_id}: {str(e)}")
        return None

def train_waste_model(merged_data):
    """Train waste prediction model"""
    if merged_data.empty or len(merged_data) < 10:
        print("Insufficient data for training")
        return None
    
    features = merged_data[['stock_level', 'days_until_expiry', 'predicted_demand', 'quantity_sold']]
    target = merged_data['quantity_wasted']

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(f"Waste Prediction MAE: {mean_absolute_error(y_test, preds):.2f}")
    return model

def generate_recommendations(model, ingredient_data):
    """Generate inventory recommendations"""
    try:
        prediction = model.predict(ingredient_data[['stock_level', 'days_until_expiry', 'predicted_demand', 'quantity_sold']])
        current_stock = ingredient_data['stock_level'].iloc[0]
        predicted_demand = ingredient_data['predicted_demand'].iloc[0]
        
        return {
            'ideal_stock': round(predicted_demand + prediction[0]),
            'predicted_waste': round(prediction[0], 2),
            'reorder_quantity': max(0, round(predicted_demand + prediction[0] - current_stock))
        }
    except Exception as e:
        print(f"Recommendation error: {str(e)}")
        return None

def main():
    data = fetch_data_from_db()
    if not data:
        return
    
    sales, inventory, waste, demand_forecast, ingredients = data
    merged_data, daily_sales = preprocess_data(sales, inventory, waste, demand_forecast, ingredients)

    waste_model = train_waste_model(merged_data)
    if not waste_model:
        return

    results = []
    for ingredient_id in merged_data['ingredient_id'].unique():
        ingredient_data = merged_data[merged_data['ingredient_id'] == ingredient_id].copy()
        sales_data = daily_sales[daily_sales['ingredient_id'] == ingredient_id]

        latest_forecast = demand_forecasting(ingredient_id, sales_data)
        if latest_forecast is None:
            latest_forecast = demand_forecast[demand_forecast['ingredient_id'] == ingredient_id]['predicted_demand'].iloc[0]

        ingredient_data['predicted_demand'] = latest_forecast
        rec = generate_recommendations(waste_model, ingredient_data)

        if rec:
            results.append({
                'ingredient_id': ingredient_id,
                'ingredient_name': ingredient_data['name'].iloc[0],
                **rec
            })

    if results:
        results_df = pd.DataFrame(results)
        print("\nAI-Powered Inventory Recommendations:")
        print(results_df.to_string(index=False))
    else:
        print("No recommendations generated")

if __name__ == "__main__":
    main()
