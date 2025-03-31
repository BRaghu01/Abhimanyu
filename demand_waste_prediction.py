import create_connection as cc
import pandas as pd
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from datetime import datetime
import mysql.connector

def fetch_data_from_db():
    """Fetch data from database with enhanced error handling"""
    conn = None
    try:
        conn = cc.create_connection()
        if not conn or not conn.is_connected():
            print("Database connection failed")
            return None

        cursor = conn.cursor(dictionary=True)
        
        # Verify tables exist
        cursor.execute("SHOW TABLES")
        existing_tables = {table['Tables_in_smart_kitchen'] for table in cursor}
        required_tables = {'sales', 'inventory', 'waste', 'demandforecast', 'ingredients'}
        
        if missing := required_tables - existing_tables:
            print(f"Missing tables: {', '.join(missing)}")
            return None

        # Fetch data using pandas
        data = {}
        for table in required_tables:
            data[table] = pd.read_sql(f"SELECT * FROM {table}", conn)
        
        return (
            data['sales'], 
            data['inventory'], 
            data['waste'],
            data['demandforecast'], 
            data['ingredients']
        )

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def preprocess_data(sales, inventory, waste, demand_forecast, ingredients):
    """Data preprocessing with column validation"""
    try:
        # Merge datasets
        inventory_merged = pd.merge(
            inventory, 
            ingredients,
            on='ingredient_id',
            suffixes=('_inv', '_ing')
        )  # Fixed missing parenthesis here
        
        # Process dates
        today = datetime.now().date()
        sales['sale_date'] = pd.to_datetime(sales['sale_date'])
        inventory_merged['expiry_date'] = pd.to_datetime(inventory_merged['expiry_date_inv'])
        
        # Create features
        daily_sales = sales.groupby(['ingredient_id', 'sale_date'])['quantity_sold'].sum().reset_index()
        
        # Merge all data
        merged = pd.merge(
            inventory_merged,
            waste[['ingredient_id', 'quantity_wasted', 'reason']],
            on='ingredient_id',
            how='left'
        )
        merged = pd.merge(
            merged,
            demand_forecast[['ingredient_id', 'predicted_demand']],
            on='ingredient_id',
            how='left'
        )
        
        # Calculate time features
        merged['days_until_expiry'] = (merged['expiry_date'] - pd.to_datetime(today)).dt.days
        merged['quantity_wasted'] = merged['quantity_wasted'].fillna(0)
        merged['reason'] = merged['reason'].fillna('No Waste')
        
        return merged, daily_sales
    
    except KeyError as e:
        print(f"Missing column in data: {e}")
        return None, None

def demand_forecasting(ingredient_id, sales_data):
    """Robust demand forecasting with Prophet"""
    try:
        if len(sales_data) < 5:
            raise ValueError("Insufficient historical data")
            
        df = sales_data.rename(columns={'sale_date': 'ds', 'quantity_sold': 'y'})
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=7)
        return model.predict(future)['yhat'].iloc[-1]
    
    except Exception as e:
        print(f"Forecasting error for ingredient {ingredient_id}: {str(e)}")
        return None

def train_waste_model(merged_data):
    """Train waste prediction model with validation"""
    try:
        required_cols = ['stock_level', 'days_until_expiry', 'predicted_demand', 'quantity_sold']
        if not all(col in merged_data.columns for col in required_cols):
            raise ValueError("Missing required columns in training data")
        
        X = merged_data[required_cols]
        y = merged_data['quantity_wasted']
        
        if len(X) < 10:
            raise ValueError("Insufficient training samples")
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        model = RandomForestRegressor(n_estimators=100)
        model.fit(X_train, y_train)
        
        print(f"Model MAE: {mean_absolute_error(y_test, model.predict(X_test)):.2f}")
        return model
    
    except Exception as e:
        print(f"Training error: {str(e)}")
        return None

def generate_recommendations(model, ingredient_data):
    """Generate recommendations with validation"""
    try:
        if not isinstance(ingredient_data, pd.DataFrame) or ingredient_data.empty:
            raise ValueError("Invalid ingredient data")
            
        required_cols = ['stock_level', 'predicted_demand']
        if not all(col in ingredient_data.columns for col in required_cols):
            raise ValueError("Missing required columns in input data")
        
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
    """Main execution flow with error handling"""
    try:
        data = fetch_data_from_db()
        if not data:
            return
            
        sales, inventory, waste, demand_forecast, ingredients = data
        
        merged_data, daily_sales = preprocess_data(sales, inventory, waste, demand_forecast, ingredients)
        if merged_data is None:
            return
            
        waste_model = train_waste_model(merged_data)
        if not waste_model:
            return
            
        results = []
        for ingredient_id in merged_data['ingredient_id'].unique():
            ingredient_data = merged_data[merged_data['ingredient_id'] == ingredient_id].copy()
            sales_data = daily_sales[daily_sales['ingredient_id'] == ingredient_id]
            
            # Get demand forecast
            forecast = demand_forecasting(ingredient_id, sales_data)
            if forecast is None:
                forecast = demand_forecast.loc[
                    demand_forecast['ingredient_id'] == ingredient_id,
                    'predicted_demand'
                ].values[0]
            
            ingredient_data['predicted_demand'] = forecast
            rec = generate_recommendations(waste_model, ingredient_data)
            
            if rec:
                results.append({
                    'ingredient_id': ingredient_id,
                    'ingredient_name': ingredient_data['name'].iloc[0],
                    **rec
                })
        
        if results:
            print("\nAI-Powered Inventory Recommendations:")
            print(pd.DataFrame(results).to_string(index=False))
        else:
            print("No recommendations generated")
    
    except Exception as e:
        print(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()