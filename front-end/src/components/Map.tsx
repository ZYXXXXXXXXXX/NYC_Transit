import React, { useEffect, useState, useRef } from 'react';
import GoogleMapReact from 'google-map-react';
import Marker from './Marker';

interface MapProps {
  center: { lat: number; lng: number };
  zoom: number;
}

// Store multi-line data (color and coordinate)
interface LineData {
  color: string;
  path: Array<{ lat: number; lng: number }>;
}

export default function SubwayMap() {
  const [stations, setStations] = useState([]);
  const [lineCoordinates, setLineCoordinates] = useState<LineData[]>([]);
  const currentLinesRef = useRef<google.maps.Polyline[]>([]);

  const mapRef = useRef(null);   // Used to store map instance
  const mapsRef = useRef(null);  // Used to store maps object (google.maps)

  // Used to store currently drawn lines on the map, for easy clearing/updating when clicking other stations
  const currentLineRef = useRef(null);

  // 1. Fetch subway station data during initialization
  useEffect(() => {
    async function fetchStations() {
      try {
        const res = await fetch('http://127.0.0.1:5000/api/stations');
        const data = await res.json();
        setStations(data);
      } catch (err) {
        console.error('Error fetching station information', err);
      }
    }
    fetchStations();
  }, []);

  // 2. When clicking a Marker, request the complete route data for that station from the backend
  const handleMarkerClick = async (stationId: string) => {
    try {
      // 1. Get route information for this station
      const routesRes = await fetch(`http://127.0.0.1:5000/api/stations/${stationId}/routes`);
      const routesData = await routesRes.json();
      const routes = routesData.routes;
  
      // 2. Get global station-route mapping relationship
      const stationRouteMapRes = await fetch('http://127.0.0.1:5000/api/station-route-map');
      const stationRouteMap = await stationRouteMapRes.json();
  
      // 3. Construct path data for each route
      const newLineCoordinates: LineData[] = routes.map(route => {
        // Find all station keys containing current route id
        const stationIds = Object.keys(stationRouteMap).filter(stationKey => {
          return stationRouteMap[stationKey].includes(route.id);
        });
  
        // Filter corresponding coordinates from stations state based on stationIds
        const path = stationIds
          .map(id => stations.find(s => s.id === id))
          .filter(Boolean) // Exclude unfound data
          // If sorting is needed, can sort according to some order field of stations
          .map(station => ({ lat: station.lat, lng: station.lng }));
  
        return {
          color: `#${route.color}`,
          path,
        };
      });
  
      // 4. Update state, trigger route drawing
      setLineCoordinates(newLineCoordinates);
    } catch (err) {
      console.error('Error fetching route data', err);
    }
  };

  // 3. Listen to lineCoordinates changes, once new route data is available, use native API to draw
useEffect(() => {
  if (!mapRef.current || !mapsRef.current || lineCoordinates.length === 0) return;

  // Clear previous lines
  if (currentLinesRef.current.length > 0) {
    currentLinesRef.current.forEach(line => line.setMap(null));
    currentLinesRef.current = [];
  }

  // Draw new lines
  const newLines = lineCoordinates.map(line => {
    return new mapsRef.current.Polyline({
      path: line.path,
      geodesic: true,
      strokeColor: line.color,
      strokeOpacity: 1.0,
      strokeWeight: 4,
    });
  });

  // Add new lines to map and save reference
  newLines.forEach(line => line.setMap(mapRef.current));
  currentLinesRef.current = newLines;

}, [lineCoordinates]);


  // 4. Google Map's onGoogleApiLoaded callback
  const handleApiLoaded = ({ map, maps }) => {
    mapRef.current = map;
    mapsRef.current = maps;
  };

  return (
    <div style={{ height: '90vh', width: '100%' }}>
      <GoogleMapReact
        bootstrapURLKeys={{ key: process.env.REACT_APP_GOOGLE_MAPS_API_KEY || '' }}
        defaultCenter={{ lat: 40.714, lng: -74.001 }} // Default center point can be customized
        defaultZoom={14}                            // Default zoom level
        options={{
          mapId: '84a43dd24922060d', 
        }}
        yesIWantToUseGoogleMapApiInternals
        onGoogleApiLoaded={handleApiLoaded}
      >
        {stations.map((station) => (
          <Marker
            key={station.id}
            lat={station.lat}
            lng={station.lng}
            text={station.name}
            onClick={() => handleMarkerClick(station.id)}
          />
        ))}
      </GoogleMapReact>
    </div>
  );
};