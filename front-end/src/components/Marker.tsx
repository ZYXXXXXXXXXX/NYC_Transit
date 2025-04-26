import React from 'react';
import MyLocationIcon from '@mui/icons-material/MyLocation';

interface MarkerProps {
    lat: number;
    lng: number;
    text?: string;
    onClick?: () => void;
    type?: 'station' | 'user';
}

const Marker: React.FC<MarkerProps> = ({ text, onClick, type }) => {
    return (
        <div 
            onClick={onClick} 
            style={{ 
            cursor: 'pointer', 
            display: 'flex', 
            alignItems: 'center' 
          }}>
            {type === 'user' ? (
                <MyLocationIcon color="primary" />
            ) : (
            <img src="/marker.png" style={{ width: 24 }} />
            )}
            <span style={{ fontWeight: 'bold'}}>{text || '📍'}</span>
        </div>
    )
}

export default Marker