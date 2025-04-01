import React from 'react';

interface MarkerProps {
    lat: number;
    lng: number;
    text?: string;
    onClick?: () => void;
}

const Marker: React.FC<MarkerProps> = ({ text, onClick }) => {
    return (
        <div 
            onClick={onClick} 
            style={{ 
            cursor: 'pointer', 
            display: 'flex', 
            alignItems: 'center' 
          }}>
            <img 
            style={{ width: '24px', height: '24px' }} 
            src="/marker.png" alt="marker" />
            <span style={{ fontWeight: 'bold'}}>{text || '📍'}</span>
        </div>
    )
}

export default Marker