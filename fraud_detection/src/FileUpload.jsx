import React, { useState } from 'react';
import axios from 'axios';
import './FileUpload.css';  // Add this import for styling

export default function FileUpload() {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            setMessage('Please select a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:8000/upload', formData);
            setMessage(response.data.message);
        } catch (error) {
            console.error('Error uploading file:', error);
            setMessage('Failed to upload file.');
        }
    };

    return (
        <div className="app-container">
            <p className="title">upload the csv here </p>
            <div className="file-upload-container">
                <input 
                    type="file" 
                    accept=".csv" 
                    onChange={handleFileChange} 
                />
                <button onClick={handleUpload}>Upload</button>
                {message && (
                    <pre style={{ borderColor: message.includes("successfully") ? '#4caf50' : '#f44336' }}>
                        {message}
                    </pre>
                )}
            </div>
        </div>
    );
}
