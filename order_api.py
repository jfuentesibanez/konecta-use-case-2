# order_api.py
# pip install fastapi uvicorn pandas kagglehub python-multipart  (en local)
# en Cloud Run / Railway basta añadir estos deps al requirements.txt

import pandas as pd
import kagglehub
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Order-Status API")

# 1️⃣  Descarga / cachea el CSV de Kaggle
path = kagglehub.dataset_download("zahidmughal2343/amazon-sales-2025")
orders_csv = next(p for p in path.rglob("*.csv"))   # primer csv encontrado
df = pd.read_csv(orders_csv, dtype=str).set_index("Order ID")

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    if order_id not in df.index:
        raise HTTPException(status_code=404, detail="Order not found")

    row = df.loc[order_id]
    # Devuelve sólo lo que necesitas para la demo
    return {
        "order_id": order_id,
        "status": row.get("Status", "Shipped"),
        "eta_days": row.get("ETA (days)", "3"),
        "item": row.get("Product Name", "Item")
    }
