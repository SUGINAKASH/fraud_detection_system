import React, { useEffect, useState } from 'react';

export default function ShapPlot() {
    const [imageSrc, setImageSrc] = useState('');

    useEffect(() => {
        setImageSrc('http://localhost:8000/shap-plot');
    }, []);

    return (
        <div>
            <h2>SHAP Summary Plot</h2>
            <img src={imageSrc} alt="SHAP Plot" style={{ width: '100%', borderRadius: '8px' }} />
        </div>
    );
}
