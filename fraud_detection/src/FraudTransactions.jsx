import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function FraudTransactions() {
    const [transactions, setTransactions] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:8000/fraud-transactions')
            .then(response => setTransactions(response.data))
            .catch(error => console.error('Error fetching transactions:', error));
    }, []);

    return (
        <div>
            <h2>Fraudulent Transactions</h2>
            <pre>{JSON.stringify(transactions, null, 2)}</pre>
        </div>
    );
}
