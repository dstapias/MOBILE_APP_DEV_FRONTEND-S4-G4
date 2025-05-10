from flask import Flask, jsonify
import pandas as pd
import requests
import numpy as np

app = Flask(__name__)
baseUrl = 'https://baf8-181-237-22-203.ngrok-free.app/api'

@app.route("/powerbi-data", methods=["GET"])
def powerbi_data():
    # 1. Obtener órdenes
    orders_response = requests.get(f"{baseUrl}/orders/")
    orders = orders_response.json()
    df_orders = pd.DataFrame(orders)

    # 2. Filtrar solo BILLED
    billed_orders = df_orders[df_orders["status"] == "Status.BILLED"]

    # 3. Obtener todos los productos (una sola vez)
    products_response = requests.get(f"{baseUrl}/products/")
    products = products_response.json()
    df_products = pd.DataFrame(products)

    resultados = []

    # 4. Para cada orden facturada, traer productos del carrito
    for _, order in billed_orders.iterrows():
        cart_id = order["cart_id"]
        billed_date = order["billed_date"]

        cart_products_response = requests.get(f"{baseUrl}/cart_products/cart/{cart_id}")
        cart_products = cart_products_response.json()

        for item in cart_products:
            product_id = item["product_id"]
            quantity = item["quantity"]

            # Buscar el nombre del producto y precio
            product_info = df_products[df_products["product_id"] == product_id]
            if not product_info.empty:
                product_name = product_info.iloc[0]["name"]
                unit_price = product_info.iloc[0]["unit_price"]
            else:
                product_name = "Unknown"
                unit_price = 0.0

            resultados.append({
                "cart_id": cart_id,
                "product_id": product_id,
                "product_name": product_name,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": quantity * unit_price,
                "billed_date": billed_date
            })

    # 5. Convertir resultados
    final_df = pd.DataFrame(resultados)

    return jsonify(final_df.to_dict(orient="records"))

@app.route("/signup-attempts", methods=["GET"])
def signup_attempts():
    try:
        signup_response = requests.get(f"{baseUrl}/users/signup_events")
        attempts = signup_response.json()

        df = pd.DataFrame(attempts)

        # Convertir fechas
        df['started_at'] = pd.to_datetime(df['started_at'], errors='coerce')
        df['completed_at'] = pd.to_datetime(df['completed_at'], errors='coerce')

        # Calcular duración
        df['duration_minutes'] = (df['completed_at'] - df['started_at']).dt.total_seconds() / 60
        df['completed'] = df['completed_at'].notna()

        # Convertir fechas a string, NaT se vuelve None
        df['started_at'] = df['started_at'].apply(lambda x: x.isoformat() if pd.notnull(x) else None)
        df['completed_at'] = df['completed_at'].apply(lambda x: x.isoformat() if pd.notnull(x) else None)

        # Reemplazar NaN con None
        df = df.replace({np.nan: None})

        return jsonify(df.to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)