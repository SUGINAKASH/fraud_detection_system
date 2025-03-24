from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
from io import StringIO

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import LocalOutlierFactor

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable for processed data
original_data = None  # Store non-scaled data
processed_data = None

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global processed_data, original_data
    if file.filename.endswith('.csv'):
        contents = await file.read()
        try:
            df = pd.read_csv(StringIO(contents.decode('utf-8')))
        except Exception as e:
            return JSONResponse(content={"error": f"Error reading file: {str(e)}"}, status_code=400)

        if 'Transaction_ID' not in df.columns:
            df['Transaction_ID'] = np.arange(1, len(df) + 1)  # Add Transaction_ID if missing

        original_data = df.copy()  # Save original data for transaction IDs

        # Identify categorical columns and apply Label Encoding
        categorical_cols = df.select_dtypes(include=["object"]).columns
        label_encoders = {}
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))  # Ensure strings for compatibility
            label_encoders[col] = le

        # Normalize numerical features
        scaler = StandardScaler()
        df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

        # Apply LOF
        lof = LocalOutlierFactor(n_neighbors=20, contamination=0.02)
        df_scaled["LOF_Anomaly"] = lof.fit_predict(df_scaled)

        # Apply Isolation Forest
        iso_forest = IsolationForest(n_estimators=200, contamination=0.02, random_state=42)
        df_scaled["IF_Anomaly"] = iso_forest.fit_predict(df_scaled)

        # Convert anomaly labels (-1 -> Fraud, 1 -> Normal)
        df_scaled["LOF_Anomaly"] = df_scaled["LOF_Anomaly"].apply(lambda x: 1 if x == -1 else 0)
        df_scaled["IF_Anomaly"] = df_scaled["IF_Anomaly"].apply(lambda x: 1 if x == -1 else 0)

        # Final Fraud Label
        df_scaled["Fraud_Label"] = (df_scaled["LOF_Anomaly"] & df_scaled["IF_Anomaly"])

        # Save processed data for future endpoints
        processed_data = df_scaled.copy()

        return JSONResponse(content={"message": "File uploaded successfully!"})

    else:
        return JSONResponse(content={"error": "Only CSV files are supported"}, status_code=400)

@app.get("/fraud-transactions")
async def get_fraud_transactions():
    if processed_data is None or original_data is None:
        return JSONResponse(content={"error": "No data available. Please upload a file first."}, status_code=400)

    fraud_indices = processed_data[processed_data["Fraud_Label"] == 1].index
    fraud_transactions = original_data.loc[fraud_indices, 'Transaction_ID'].tolist()
    return JSONResponse(content=fraud_transactions)

@app.get("/shap-plot")
async def get_shap_plot():
    if processed_data is None:
        return JSONResponse(content={"error": "No data available. Please upload a file first."}, status_code=400)

    # Define supervised models
    X = processed_data.drop(columns=["Fraud_Label"])
    y = processed_data["Fraud_Label"]

    xgb = XGBClassifier(n_estimators=200, learning_rate=0.05, max_depth=6)
    xgb.fit(X, y)

    explainer = shap.TreeExplainer(xgb)
    shap_values = explainer.shap_values(X)

    # Generate and save the SHAP summary plot
    plt.title("SHAP Summary Plot")
    shap.summary_plot(shap_values, X, show=False)
    plt.savefig("shap_summary_plot.png")
    plt.close()

    return FileResponse("shap_summary_plot.png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
