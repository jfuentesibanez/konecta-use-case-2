# order_api.py
# FastAPI micro-backend for “Konecta order status” demo
# -----------------------------------------------------
# • Downloads the public Kaggle dataset once (cached)
# • Exposes GET /orders/{order_id}
# • Returns simple JSON the Twilio Function can read
#
# Run locally:
#   uvicorn order_api:app --port 8000 --host 0.0.0.0
#
# Deploy on Railway / Render / Cloud Run:
#   requirements.txt + Procfile are enough (see previous instructions)

from pathlib import Path
import pandas as pd
import kagglehub
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Order-Status API", version="0.1.0")

# --------------------------------------------------------------------
# 1) Download (or reuse cached) Kaggle dataset
# --------------------------------------------------------------------
DATASET = "zahidmughal2343/amazon-sales-2025"          # ↙ change if you switch datasets
dataset_root = Path(kagglehub.dataset_download(DATASET))

# Find the first CSV inside the dataset folder tree
csv_files = list(dataset_root.rglob("*.csv"))
if not csv_files:
    raise RuntimeError(f"No CSV found in Kaggle dataset {DATASET}")

orders_csv = csv_files[0]

# --------------------------------------------------------------------
# 2) Load into pandas DataFrame
# --------------------------------------------------------------------
df = pd.read_csv(orders_csv, dtype=str)

# Pick the correct column as primary key (“Order ID”, “order_id”, etc.)
id_col_candidates = ["Order ID", "Order_ID", "order_id", "order ID"]
id_col = next((c for c in id_col_candidates if c in df.columns), None)
if id_col is None:
    raise RuntimeError("CSV missing an Order-ID column")

df.set_index(id_col, inplace=True)

# --------------------------------------------------------------------
# 3) Endpoints
# --------------------------------------------------------------------
@app.get("/healthz", tags=["meta"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok"}


@app.get("/orders/{order_id}", tags=["orders"])
def get_order(order_id: str):
    """Return status info for a single order."""
    if order_id not in df.index:
        raise HTTPException(status_code=404, detail="Order not found")

    row = df.loc[order_id]
    return {
        "order_id": order_id,
        "status": row.get("Status", "Shipped"),
        "eta_days": row.get("ETA (days)", "3"),
        "item": row.get("Product Name", "Item"),
    }
