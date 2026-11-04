

- Used data/processed/cleaned_sales.csv (chronological order to avoid leakage)
- Assumption: Lead Time=3 days, Review Period=7 days, Service Level Z=1.65 (95%) - Lead time not in dataset
- Formulas: Safety Stock = Z * std * sqrt(LT+Review), Reorder Point = Avg*LT + Safety Stock
- Output: reports/inventory_recommendations.csv with 200 rows
- Note: Used Demand column not Units Sold as per warning
- Status logic: REORDER NOW / LOW STOCK / SUFFICIENT
  
pip install -r requirements.txt
python src/inventory_optimization.py
