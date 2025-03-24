import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import FileUpload from "./FileUpload";
import FraudTransactions from "./FraudTransactions";
import ShapPlot from "./ShapPlot";
import "./styles.css";  

export default function App() {
    return (
        <Router>
            <div className="app-container">
                <div className="file-upload-container">
                    <h1 className="title">Fraud Detection System</h1>
                    <FileUpload />
                </div>

                <div className="nav-container">
                    <p>results:</p>
                    <Link to="/fraud-transactions" className="nav-button">Fraud Transactions</Link>
                    <Link to="/shap-plot" className="nav-button">SHAP Plot</Link>
                </div>

                <Routes>
                    <Route path="/fraud-transactions" element={<FraudTransactions />} />
                    <Route path="/shap-plot" element={<ShapPlot />} />
                </Routes>
            </div>
        </Router>
    );
}
