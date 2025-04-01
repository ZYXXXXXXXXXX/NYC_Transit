// Map.tsx (TypeScript)
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

  const mapRef = useRef(null);   // 用来保存 map 实例
  const mapsRef = useRef(null);  // 用来保存 maps 对象（google.maps）

  // 用来保存当前绘制在地图上的线路，方便在点击其他站台时清除或更新
  const currentLineRef = useRef(null);

  // 1. 初始化时获取地铁站点数据
  useEffect(() => {
    async function fetchStations() {
      try {
        const res = await fetch('http://127.0.0.1:5000/api/stations');
        const data = await res.json();
        setStations(data);
      } catch (err) {
        console.error('获取站点信息出错', err);
      }
    }
    fetchStations();
  }, []);

  // 2. 点击某个 Marker 时，向后端请求该站的整条线路数据
  const handleMarkerClick = async (stationId: string) => {
    try {
      // 1. 获取该站点的线路信息
      const routesRes = await fetch(`http://127.0.0.1:5000/api/stations/${stationId}/routes`);
      const routesData = await routesRes.json();
      const routes = routesData.routes;
  
      // 2. 获取全局站点和线路的映射关系
      const stationRouteMapRes = await fetch('http://127.0.0.1:5000/api/station-route-map');
      const stationRouteMap = await stationRouteMapRes.json();
  
      // 3. 为每个线路构造路径数据
      const newLineCoordinates: LineData[] = routes.map(route => {
        // 找出所有包含当前线路 id 的站点 key
        const stationIds = Object.keys(stationRouteMap).filter(stationKey => {
          return stationRouteMap[stationKey].includes(route.id);
        });
  
        // 根据 stationIds 从 stations 状态中过滤出对应的坐标
        const path = stationIds
          .map(id => stations.find(s => s.id === id))
          .filter(Boolean) // 排除未找到的数据
          // 如果需要排序，可根据站点的某个顺序字段进行排序
          .map(station => ({ lat: station.lat, lng: station.lng }));
  
        return {
          color: `#${route.color}`,
          path,
        };
      });
  
      // 4. 更新 state，触发线路绘制
      setLineCoordinates(newLineCoordinates);
    } catch (err) {
      console.error('获取线路数据出错', err);
    }
  };

  // 3. 监听 lineCoordinates 变化，一旦有新线路数据，就用原生 API 进行绘制
// Map.tsx
useEffect(() => {
  if (!mapRef.current || !mapsRef.current || lineCoordinates.length === 0) return;

  // 清理之前的线路
  if (currentLinesRef.current.length > 0) {
    currentLinesRef.current.forEach(line => line.setMap(null));
    currentLinesRef.current = [];
  }

  // 绘制新线路
  const newLines = lineCoordinates.map(line => {
    return new mapsRef.current.Polyline({
      path: line.path,
      geodesic: true,
      strokeColor: line.color,
      strokeOpacity: 1.0,
      strokeWeight: 4,
    });
  });

  // 将新线路添加到地图并保存引用
  newLines.forEach(line => line.setMap(mapRef.current));
  currentLinesRef.current = newLines;

}, [lineCoordinates]);


  // 4. Google Map 的 onGoogleApiLoaded 回调
  const handleApiLoaded = ({ map, maps }) => {
    mapRef.current = map;
    mapsRef.current = maps;
  };

  return (
    <div style={{ height: '90vh', width: '100%' }}>
      <GoogleMapReact
        bootstrapURLKeys={{ key: process.env.REACT_APP_GOOGLE_MAPS_API_KEY || '' }}
        defaultCenter={{ lat: 40.714, lng: -74.001 }} // 默认中心点可自行设置
        defaultZoom={14}                            // 默认缩放级别
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