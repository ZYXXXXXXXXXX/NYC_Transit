import React, { useEffect, useState, useRef } from 'react';
import GoogleMapReact from 'google-map-react';
import Marker from './Marker';
import StationInfoDialog from '../pages/StationInfoDialog';
import { SubwayRoute, Station } from '~/types/api';

interface MapProps {
  center: { lat: number; lng: number };
  zoom: number;
}

// Data structure to store subway line information (color and coordinates)
interface LineData {
  color: string;
  path: Array<{ lat: number; lng: number }>;
}

export default function SubwayMap(props: MapProps) {
  const [stations, setStations] = useState<Station[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [lineCoordinates, setLineCoordinates] = useState<LineData[]>([]);
  const [selectedStationInfo, setSelectedStationInfo] = useState<Station | null>(null);
  
  // Refs to store Google Maps objects and drawn polylines
  const currentLinesRef = useRef<google.maps.Polyline[]>([]);
  const mapRef = useRef(null);     // Reference to Google Map instance
  const mapsRef = useRef(null);    // Reference to Google Maps API

  // Fetch all subway stations when component mounts
  useEffect(() => {
    async function fetchStations() {
      try {
        const res = await fetch('http://127.0.0.1:5000/api/stations');
        const data = await res.json();
        console.log('Fetched stations:', data);
        setStations(data);
      } catch (err) {
        console.error('Error fetching station information', err);
      }
    }
    fetchStations();
  }, []);

  /**
   * Handles marker click event:
   * 1. Fetches station info and associated routes
   * 2. Gets all stops for each route
   * 3. Prepares line coordinates for drawing
   * 4. Opens station info dialog
   */
  const handleMarkerClick = async (stationId: string) => {
    try {
      // Get station info and its associated routes
      const infoRes = await fetch(`http://127.0.0.1:5000/api/stations/${stationId}/routes`);
      const stationInfo = await infoRes.json();
      const routes: SubwayRoute[] = stationInfo.routes;

      // Fetch all stops for each route in parallel
      const routesWithStops = await Promise.all(
        routes.map(async (route) => {
          const stopsRes = await fetch(`http://127.0.0.1:5000/api/routes/${route.id}/stops`);
          const stopsData = await stopsRes.json();
          return { 
            route, 
            path: stopsData.stops.map(stop => ({ lat: stop.lat, lng: stop.lng }))
          };
        })
      );

      // Prepare line data for each route (color + coordinates)
      const newLineCoordinates: LineData[] = routesWithStops.map(({ route, path }) => ({
        color: `#${route.color}`,  // Convert color code to hex format
        path: path
      }));

      // Update state to trigger line drawing
      setLineCoordinates(newLineCoordinates);
      
      // Prepare station info for the dialog
      setSelectedStationInfo({
        id: stationId,
        name: stationInfo.name,
        routes: routes.map(r => ({ id: r.id, color: r.color }))
      });
      
      // Open the station info dialog
      setDialogOpen(true);
    } catch (err) {
      console.error('Error fetching route data', err);
    }
  };

  /**
   * Effect to draw polylines when lineCoordinates changes:
   * 1. Clears existing lines
   * 2. Draws new lines based on current coordinates
   */
  useEffect(() => {
    // Skip if required objects aren't initialized or no lines to draw
    if (!mapRef.current || !mapsRef.current || lineCoordinates.length === 0) return;

    // Clear all existing lines from the map
    currentLinesRef.current.forEach(line => line.setMap(null));
    currentLinesRef.current = [];

    // Create new polylines for each route
    const newLines = lineCoordinates.map(line => {
      return new mapsRef.current.Polyline({
        path: line.path,          // Array of coordinates
        geodesic: true,            // Follows Earth's curvature
        strokeColor: line.color,    // Line color from route data
        strokeOpacity: 1.0,         // Fully opaque
        strokeWeight: 4,           // Line thickness
      });
    });

    // Add all new lines to the map and store references
    newLines.forEach(line => line.setMap(mapRef.current));
    currentLinesRef.current = newLines;
  }, [lineCoordinates]);

  // Callback when Google Maps API loads - stores map references
  const handleApiLoaded = ({ map, maps }) => {
    mapRef.current = map;
    mapsRef.current = maps;
  };

  return (
    <div style={{ height: '90vh', width: '100%' }}>
      <GoogleMapReact
        bootstrapURLKeys={{ key: process.env.REACT_APP_GOOGLE_MAPS_API_KEY || '' }}
        defaultCenter={{ lat: 40.714, lng: -74.001 }}  // Default NYC coordinates
        defaultZoom={14}                                // Medium zoom level
        options={{ mapId: '84a43dd24922060d' }}         // Custom map style ID
        yesIWantToUseGoogleMapApiInternals
        onGoogleApiLoaded={handleApiLoaded}
      >
        {/* Render markers for all stations */}
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
      
      {/* Station information dialog */}
      <StationInfoDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        station={selectedStationInfo}
      />
    </div>
  );
};