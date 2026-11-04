import pandas as pd
import numpy as np
import os

# PATHS
cleaned_path1 = "data/processed/cleaned_sales.csv"
cleaned_path2 = "data/processed/cleaned_data.csv"
raw_path = "data/raw/sales_data.csv"
output_path = "reports/inventory_recommendations.csv"

# Assumptions 
LEAD_TIME_DAYS = 3
REVIEW_PERIOD_DAYS = 7
SERVICE_LEVEL_Z = 1.65
LOOKBACK_DAYS = 28

# LOAD
df = None
for p in [cleaned_path1, cleaned_path2, raw_path]:
    if os.path.exists(p):
        df = pd.read_csv(p)
        print(f"Loaded: {p}")
        break

if df is None:
    raise FileNotFoundError("Cleaned file not found at data/processed/cleaned_sales.csv")

# Chronological order 
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

# Demand vs Units Sold 
demand_col = 'Demand' if 'Demand' in df.columns else 'Units Sold'
stock_col = 'Inventory Level' if 'Inventory Level' in df.columns else 'Current_Inventory'
product_col = 'Product ID' if 'Product ID' in df.columns else 'Product_ID'
store_col = 'Store ID' if 'Store ID' in df.columns else None

os.makedirs('reports', exist_ok=True)
results = []

# Group by Store and Product
if store_col and store_col in df.columns:
    groups = df.groupby([store_col, product_col])
else:
    groups = df.groupby([product_col])

for name, group in groups:
    if isinstance(name, tuple) and len(name) == 2:
        store_id, product_id = name
    else:
        store_id = "S001"
        product_id = name if not isinstance(name, tuple) else str(name)

    recent = group.tail(LOOKBACK_DAYS)
    estimated_daily = recent[demand_col].mean()
    std_daily = recent[demand_col].std()
    if pd.isna(std_daily) or std_daily == 0:
        std_daily = estimated_daily * 0.3
    current_inv = recent[stock_col].iloc[-1] if stock_col in recent.columns else int(estimated_daily * 5)
    
    # FORMULAS 
    safety_stock = SERVICE_LEVEL_Z * std_daily * np.sqrt(LEAD_TIME_DAYS + REVIEW_PERIOD_DAYS)
    reorder_point = (estimated_daily * LEAD_TIME_DAYS) + safety_stock
    target_stock = (estimated_daily * (LEAD_TIME_DAYS + REVIEW_PERIOD_DAYS)) + safety_stock
    recommended_qty = max(0, target_stock - current_inv)
    
    if current_inv <= reorder_point:
        status = "REORDER NOW"
    elif current_inv <= reorder_point + (estimated_daily * 2):
        status = "LOW STOCK"
    else:
        status = "SUFFICIENT STOCK"
    
    results.append({
        'Store ID': store_id,
        'Product ID': product_id,
        'Current_Inventory': int(current_inv),
        'Estimated_Daily_Demand': round(estimated_daily, 2),
        'Safety_Stock': int(safety_stock),
        'Reorder_Point': int(reorder_point),
        'Target_Stock': int(target_stock),
        'Recommended_Order_Quantity': int(recommended_qty),
        'Stock_Status': status
    })

final_df = pd.DataFrame(results)
final_df.to_csv(output_path, index=False)

print("Inventory optimization completed successfully!")
print(f"File created at: {output_path}")
