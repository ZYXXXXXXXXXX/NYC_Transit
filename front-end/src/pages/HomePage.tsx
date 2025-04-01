import React from 'react'
import DateDisplay from '../components/DateDisplay'
import Map from '../components/Map';
import Title from '../styles/Title';

const HomePage: React.FC = () => {
    const defaultCenter = { lat: 40.7128, lng: -74.0060 };
    const defaultZoom = 11;
    return (
        <div>
            <Title>NYC Transit Hub</Title>
            <Map center={defaultCenter} zoom={defaultZoom} />
            <DateDisplay />
        </div>
    )
}

export default HomePage
