import requests
import datetime
import csv
import os
from google.transit import gtfs_realtime_pb2
from config import (
    SUBWAY_FEEDS, LIRR_FEEDS, MNR_FEEDS,
    SERVICE_ALERT_FEEDS, ELEVATOR_ESCALATOR_FEEDS,
    CACHE_TIMEOUT
)
from utils.cache import cache


class DataService:
    """
    Data service - handles all data retrieval and processing
    """

    def get_cache_timeout(self, category, item_id):
        """
        Get cache timeout for a specific item

        Args:
            category (str): Category ('subway', 'lirr', 'mnr', 'alerts', 'accessibility')
            item_id (str): Item ID

        Returns:
            int: Cache timeout in seconds
        """
        # Check for item-specific timeout
        specific_key = f"{item_id}"
        if specific_key in CACHE_TIMEOUT:
            return CACHE_TIMEOUT[specific_key]

        # Check for category default timeout
        category_key = f"{category}_default"
        if category_key in CACHE_TIMEOUT:
            return CACHE_TIMEOUT[category_key]

        # Return global default
        return 60  # Default 1 minute

    def get_available_feeds(self):
        """
        Get all available data feeds

        Returns:
            dict: Dictionary of feed types and IDs
        """
        return {
            "subway": list(SUBWAY_FEEDS.keys()),
            "lirr": list(LIRR_FEEDS.keys()),
            "mnr": list(MNR_FEEDS.keys()),
            "alerts": list(SERVICE_ALERT_FEEDS.keys()),
            "accessibility": list(ELEVATOR_ESCALATOR_FEEDS.keys())
        }

    def get_subway_feeds(self):
        """
        Get all available subway feeds

        Returns:
            dict: Dictionary of subway feed IDs and URLs
        """
        return SUBWAY_FEEDS

    def parse_gtfs_rt(self, content, feed_id):
        """
        Parse GTFS-RT data

        Args:
            content (bytes): GTFS-RT binary content
            feed_id (str): Feed ID

        Returns:
            dict: Parsed data
        """
        try:
            # Parse GTFS-RT data
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(content)

            # Convert to JSON-serializable format
            result = {
                "header": {
                    "timestamp": feed.header.timestamp,
                    "human_time": datetime.datetime.fromtimestamp(feed.header.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                    "feed_id": feed_id
                },
                "entities": []
            }

            # Process each entity (vehicle, trip update, alert)
            for entity in feed.entity:
                entity_data = {"id": entity.id}

                # Process vehicle positions
                if entity.HasField('vehicle'):
                    vehicle = entity.vehicle
                    vehicle_data = {
                        "trip": {
                            "trip_id": vehicle.trip.trip_id,
                            "route_id": vehicle.trip.route_id
                        },
                        "timestamp": vehicle.timestamp
                    }

                    if vehicle.timestamp:
                        vehicle_data["human_time"] = datetime.datetime.fromtimestamp(vehicle.timestamp).strftime(
                            '%Y-%m-%d %H:%M:%S')

                    if vehicle.HasField('position'):
                        vehicle_data["position"] = {
                            "latitude": vehicle.position.latitude,
                            "longitude": vehicle.position.longitude
                        }

                        if vehicle.position.HasField('bearing'):
                            vehicle_data["position"]["bearing"] = vehicle.position.bearing

                        if vehicle.position.HasField('speed'):
                            vehicle_data["position"]["speed"] = vehicle.position.speed

                    if vehicle.HasField('current_status'):
                        status_mapping = {
                            0: "INCOMING_AT",
                            1: "STOPPED_AT",
                            2: "IN_TRANSIT_TO"
                        }
                        vehicle_data["current_status"] = status_mapping.get(vehicle.current_status, "UNKNOWN")

                    if vehicle.HasField('stop_id'):
                        vehicle_data["stop_id"] = vehicle.stop_id

                    entity_data["vehicle"] = vehicle_data

                # Process trip updates
                if entity.HasField('trip_update'):
                    trip_update = entity.trip_update
                    update_data = {
                        "trip": {
                            "trip_id": trip_update.trip.trip_id,
                            "route_id": trip_update.trip.route_id
                        },
                        "stop_time_updates": []
                    }

                    if trip_update.HasField('timestamp'):
                        update_data["timestamp"] = trip_update.timestamp
                        update_data["human_time"] = datetime.datetime.fromtimestamp(trip_update.timestamp).strftime(
                            '%Y-%m-%d %H:%M:%S')

                    for stop_time in trip_update.stop_time_update:
                        stop_data = {"stop_id": stop_time.stop_id}

                        if stop_time.HasField('arrival'):
                            arrival_data = {"time": stop_time.arrival.time}

                            if stop_time.arrival.time:
                                arrival_data["human_time"] = datetime.datetime.fromtimestamp(
                                    stop_time.arrival.time).strftime('%Y-%m-%d %H:%M:%S')

                            if stop_time.arrival.HasField('delay'):
                                arrival_data["delay"] = stop_time.arrival.delay

                            stop_data["arrival"] = arrival_data

                        if stop_time.HasField('departure'):
                            departure_data = {"time": stop_time.departure.time}

                            if stop_time.departure.time:
                                departure_data["human_time"] = datetime.datetime.fromtimestamp(
                                    stop_time.departure.time).strftime('%Y-%m-%d %H:%M:%S')

                            if stop_time.departure.HasField('delay'):
                                departure_data["delay"] = stop_time.departure.delay

                            stop_data["departure"] = departure_data

                        update_data["stop_time_updates"].append(stop_data)

                    entity_data["trip_update"] = update_data

                # Process alerts
                if entity.HasField('alert'):
                    alert = entity.alert
                    alert_data = {
                        "active_period": [],
                        "informed_entity": []
                    }

                    # Add basic info
                    if alert.HasField('cause'):
                        alert_data["cause"] = alert.cause

                    if alert.HasField('effect'):
                        alert_data["effect"] = alert.effect

                    # Process URL
                    if alert.HasField('url') and alert.url.translation:
                        alert_data["url"] = alert.url.translation[0].text

                    # Process title and description
                    if alert.HasField('header_text') and alert.header_text.translation:
                        alert_data["header_text"] = alert.header_text.translation[0].text

                    if alert.HasField('description_text') and alert.description_text.translation:
                        alert_data["description_text"] = alert.description_text.translation[0].text

                    # Process active periods
                    for period in alert.active_period:
                        period_data = {}

                        if period.HasField('start'):
                            period_data["start"] = {
                                "timestamp": period.start,
                                "human_time": datetime.datetime.fromtimestamp(period.start).strftime(
                                    '%Y-%m-%d %H:%M:%S')
                            }

                        if period.HasField('end'):
                            period_data["end"] = {
                                "timestamp": period.end,
                                "human_time": datetime.datetime.fromtimestamp(period.end).strftime('%Y-%m-%d %H:%M:%S')
                            }

                        alert_data["active_period"].append(period_data)

                    # Process affected entities
                    for entity in alert.informed_entity:
                        entity_info = {}

                        if entity.HasField('agency_id'):
                            entity_info["agency_id"] = entity.agency_id

                        if entity.HasField('route_id'):
                            entity_info["route_id"] = entity.route_id

                        if entity.HasField('route_type'):
                            entity_info["route_type"] = entity.route_type

                        if entity.HasField('stop_id'):
                            entity_info["stop_id"] = entity.stop_id

                        alert_data["informed_entity"].append(entity_info)

                    entity_data["alert"] = alert_data

                result["entities"].append(entity_data)

            return result

        except Exception as e:
            return {"error": f"Error parsing GTFS-RT data: {str(e)}"}

    def get_subway_feed(self, feed_id):
        """
        Get data for specific subway line group

        Args:
            feed_id (str): Subway line group ID

        Returns:
            dict: Processed subway data or error
        """
        # Validate feed_id
        if feed_id not in SUBWAY_FEEDS:
            return {"error": f"Invalid subway feed: {feed_id}"}

        # Check cache
        cache_key = f"subway_{feed_id}"
        cached_data = cache.get(cache_key, self.get_cache_timeout('subway', feed_id))
        if cached_data:
            return cached_data

        # Fetch data
        try:
            response = requests.get(SUBWAY_FEEDS[feed_id])

            if response.status_code == 200:
                # Parse GTFS-RT data
                result = self.parse_gtfs_rt(response.content, feed_id)

                # Cache result
                cache.set(cache_key, result)
                return result
            else:
                return {"error": f"HTTP error: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def get_lirr_feed(self, feed_id):
        """
        Get LIRR data

        Args:
            feed_id (str): LIRR feed ID

        Returns:
            dict: Processed LIRR data or error
        """
        # Validate feed_id
        if feed_id not in LIRR_FEEDS:
            return {"error": f"Invalid LIRR feed: {feed_id}"}

        # Check cache
        cache_key = f"lirr_{feed_id}"
        cached_data = cache.get(cache_key, self.get_cache_timeout('lirr', feed_id))
        if cached_data:
            return cached_data

        # Fetch data
        try:
            response = requests.get(LIRR_FEEDS[feed_id])

            if response.status_code == 200:
                # Parse GTFS-RT data
                result = self.parse_gtfs_rt(response.content, feed_id)

                # Cache result
                cache.set(cache_key, result)
                return result
            else:
                return {"error": f"HTTP error: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def get_mnr_feed(self, feed_id):
        """
        Get Metro-North data

        Args:
            feed_id (str): Metro-North feed ID

        Returns:
            dict: Processed Metro-North data or error
        """
        # Validate feed_id
        if feed_id not in MNR_FEEDS:
            return {"error": f"Invalid MNR feed: {feed_id}"}

        # Check cache
        cache_key = f"mnr_{feed_id}"
        cached_data = cache.get(cache_key, self.get_cache_timeout('mnr', feed_id))
        if cached_data:
            return cached_data

        # Fetch data
        try:
            response = requests.get(MNR_FEEDS[feed_id])

            if response.status_code == 200:
                # Parse GTFS-RT data
                result = self.parse_gtfs_rt(response.content, feed_id)

                # Cache result
                cache.set(cache_key, result)
                return result
            else:
                return {"error": f"HTTP error: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def get_service_alerts(self, alert_type):
        """
        Get service alerts

        Args:
            alert_type (str): Alert type

        Returns:
            dict: Service alert data or error
        """
        # Validate alert_type
        if alert_type not in SERVICE_ALERT_FEEDS:
            return {"error": f"Invalid alert type: {alert_type}"}

        # Check cache
        cache_key = f"alert_{alert_type}"
        cached_data = cache.get(cache_key, self.get_cache_timeout('alerts', alert_type))
        if cached_data:
            return cached_data

        try:
            response = requests.get(SERVICE_ALERT_FEEDS[alert_type])

            if response.status_code == 200:
                # Parse GTFS-RT data
                result = self.parse_gtfs_rt(response.content, alert_type)

                # Cache result
                cache.set(cache_key, result)
                return result
            else:
                return {"error": f"HTTP error: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def get_station_accessibility(self, station_id):
        """
        Get detailed station accessibility info

        Args:
            station_id (str): Station ID

        Returns:
            dict: Station accessibility info
        """

        equipment_data = self.get_accessibility_data('equipment')

        if "error" in equipment_data:
            return equipment_data

        current_data = self.get_accessibility_data('current')
        upcoming_data = self.get_accessibility_data('upcoming')
        station_equipment = []


        if "equipment" in equipment_data:
            for item in equipment_data["equipment"]:
                if item.get("station_id") == station_id:

                    if "elevatorId" in item and "current" in current_data:
                        for status in current_data.get("outages", []):
                            if status.get("equipment_id") == item["elevatorId"]:
                                item["status"] = status

                    station_equipment.append(item)

        # get info from stops.txt
        wheelchair_info = None
        stops_file = os.path.join('data', 'gtfs_subway', 'stops.txt')

        try:
            with open(stops_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['stop_id'] == station_id and 'wheelchair_boarding' in row:
                        wheelchair_info = {
                            "wheelchair_boarding": row['wheelchair_boarding'],
                            "wheelchair_accessible": row['wheelchair_boarding'] == "1"
                        }
                        break
        except Exception:
            pass

        # 返回结果
        return {
            "station_id": station_id,
            "equipment_count": len(station_equipment),
            "equipment": station_equipment,
            "wheelchair_info": wheelchair_info
        }

    def get_stations(self):
        """
        Get all stations data from GTFS stops.txt file

        Returns:
            list: List of station objects
        """
        # Check cache
        cache_key = "stations"
        cached_data = cache.get(cache_key, self.get_cache_timeout('stations', 'stations'))
        if cached_data:
            return cached_data

        try:
            # Load station data from stops.txt
            stops_file = os.path.join('data', 'gtfs_subway', 'stops.txt')

            stations = []

            with open(stops_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Only get stations, not entrances, platforms, etc.
                    # In GTFS, location_type=0 or unspecified means a stop or station
                    if row.get('location_type', '0') == '0' or not row.get('location_type'):
                        station = {
                            "id": row['stop_id'],
                            "name": row['stop_name'],
                            "lat": float(row['stop_lat']),
                            "lng": float(row['stop_lon'])
                        }
                        stations.append(station)

            # Cache results
            cache.set(cache_key, stations)
            return stations

        except Exception as e:
            return {"error": f"Failed to load stations data: {str(e)}"}

    def get_routes(self):
        """
        Get all routes (subway lines) data

        Returns:
            list: List of route objects
        """
        # Check cache
        cache_key = "routes"
        cached_data = cache.get(cache_key, self.get_cache_timeout('routes', 'routes'))
        if cached_data:
            return cached_data

        try:
            # Load routes data from routes.txt
            routes_file = os.path.join('data', 'gtfs_subway', 'routes.txt')

            routes = []

            with open(routes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    route = {
                        "id": row['route_id'],
                        "short_name": row['route_short_name'],
                        "long_name": row['route_long_name'],
                        "color": row.get('route_color', ''),
                        "text_color": row.get('route_text_color', '')
                    }
                    routes.append(route)

            # Cache results
            cache.set(cache_key, routes)
            return routes

        except Exception as e:
            return {"error": f"Failed to load routes data: {str(e)}"}

    def get_line_shape(self, route_id):
        """
        Get shape coordinates for a specific route

        Args:
            route_id (str): Route ID

        Returns:
            list: List of coordinate points along the route
        """
        # Check cache
        cache_key = f"line_shape_{route_id}"
        cached_data = cache.get(cache_key, self.get_cache_timeout('lines', route_id))
        if cached_data:
            return cached_data

        try:
            # Process steps:
            # 1. Get trips for this route from trips.txt
            # 2. Extract shape_ids from trips
            # 3. Get coordinates for these shapes from shapes.txt

            trips_file = os.path.join('data', 'gtfs_subway', 'trips.txt')
            shapes_file = os.path.join('data', 'gtfs_subway', 'shapes.txt')

            # Get shape_ids for this route_id
            shape_ids = set()
            with open(trips_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['route_id'] == route_id:
                        shape_ids.add(row['shape_id'])

            if not shape_ids:
                return {"error": f"No shapes found for route: {route_id}"}

            # Get coordinates for each shape
            shapes = {}
            for shape_id in shape_ids:
                shapes[shape_id] = []

            with open(shapes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['shape_id'] in shape_ids:
                        shapes[row['shape_id']].append({
                            "lat": float(row['shape_pt_lat']),
                            "lng": float(row['shape_pt_lon']),
                            "sequence": int(row['shape_pt_sequence'])
                        })

            # Sort each shape by sequence
            for shape_id in shapes:
                shapes[shape_id].sort(key=lambda x: x['sequence'])

            # Return list of coordinates for all shapes (remove sequence)
            result = {
                "route_id": route_id,
                "shapes": [{
                    "shape_id": shape_id,
                    "coordinates": [{"lat": pt["lat"], "lng": pt["lng"]} for pt in shapes[shape_id]]
                } for shape_id in shapes]
            }

            # Cache results
            cache.set(cache_key, result)
            return result

        except Exception as e:
            return {"error": f"Failed to load shape data: {str(e)}"}

    def get_line(self, line_id):
        """
        Get geographic coordinates for a specific line

        Args:
            line_id (str or int): Line ID

        Returns:
            list: List of coordinate points along the line
        """
        # Check cache
        cache_key = f"line_{line_id}"
        cached_data = cache.get(cache_key, self.get_cache_timeout('lines', line_id))
        if cached_data:
            return cached_data

        try:
            # Initialize empty result list
            coordinates = []

            # Path to GTFS files
            trips_file = os.path.join('data', 'gtfs_subway', 'trips.txt')
            shapes_file = os.path.join('data', 'gtfs_subway', 'shapes.txt')
            stops_file = os.path.join('data', 'gtfs_subway', 'stops.txt')
            stop_times_file = os.path.join('data', 'gtfs_subway', 'stop_times.txt')

            # Check if files exist
            if not os.path.exists(trips_file) or not os.path.exists(shapes_file):
                print(
                    f"Missing required files: trips={os.path.exists(trips_file)}, shapes={os.path.exists(shapes_file)}")
                return {"error": "GTFS data files not found"}

            # Step 1: Find a shape_id for this route from trips.txt
            shape_ids = set()
            with open(trips_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['route_id'] == line_id and 'shape_id' in row:
                        shape_ids.add(row['shape_id'])

            # Step 2: If we found a shape_id, get coordinates from shapes.txt
            if shape_ids:
                print(f"Found {len(shape_ids)} shape_ids for route {line_id}")

                # Get the first shape_id (could get multiple or pick longest)
                primary_shape_id = list(shape_ids)[0]

                # Get all points for this shape
                shape_points = []
                with open(shapes_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['shape_id'] == primary_shape_id:
                            shape_points.append({
                                'lat': float(row['shape_pt_lat']),
                                'lng': float(row['shape_pt_lon']),
                                'sequence': int(row['shape_pt_sequence'])
                            })

                # Sort by sequence
                shape_points.sort(key=lambda p: p['sequence'])

                # Create coordinates list (without sequence)
                coordinates = [{'lat': p['lat'], 'lng': p['lng']} for p in shape_points]

                print(f"Found {len(coordinates)} points for shape {primary_shape_id}")

            # Step 3: If no shape data, use stops
            if not coordinates:
                print(f"No shape data for route {line_id}, using stops")

                # Get trip_ids for this route
                trip_ids = set()
                with open(trips_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['route_id'] == line_id:
                            trip_ids.add(row['trip_id'])

                # If we have trips, get stops for them
                if trip_ids:
                    # Get the first trip_id to use (could pick something more representative)
                    primary_trip_id = list(trip_ids)[0]

                    # Get stop_ids for this trip
                    stop_sequence = []
                    with open(stop_times_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row['trip_id'] == primary_trip_id:
                                stop_sequence.append({
                                    'stop_id': row['stop_id'],
                                    'sequence': int(row['stop_sequence'])
                                })

                    # Sort by sequence
                    stop_sequence.sort(key=lambda s: s['sequence'])

                    # Get coordinates for these stops
                    stop_dict = {}
                    with open(stops_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            stop_dict[row['stop_id']] = {
                                'lat': float(row['stop_lat']),
                                'lng': float(row['stop_lon'])
                            }

                    # Create coordinates list from stops
                    for stop in stop_sequence:
                        if stop['stop_id'] in stop_dict:
                            coordinates.append(stop_dict[stop['stop_id']])

                    print(f"Created line from {len(coordinates)} stops")

            # Cache and return results
            if coordinates:
                cache.set(cache_key, coordinates)
                return coordinates
            else:
                return {"error": f"No data found for line {line_id}"}

        except Exception as e:
            import traceback
            print(f"Error in get_line: {str(e)}")
            print(traceback.format_exc())
            return {"error": f"Failed to load line data: {str(e)}"}

    def get_station_route_map(self):
        """
        Get mapping between stations and routes

        Returns:
            dict: Mapping of station IDs to route IDs
        """
        # Check cache
        cache_key = "station_route_map"
        cached_data = cache.get(cache_key, 86400)  # Cache for 24 hours
        if cached_data:
            return cached_data

        try:
            stop_times_file = os.path.join('data', 'gtfs_subway', 'stop_times.txt')
            trips_file = os.path.join('data', 'gtfs_subway', 'trips.txt')

            # Create stop_id to trip_id mapping from stop_times.txt
            stop_to_trips = {}
            with open(stop_times_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stop_id = row['stop_id']
                    trip_id = row['trip_id']
                    if stop_id not in stop_to_trips:
                        stop_to_trips[stop_id] = set()
                    stop_to_trips[stop_id].add(trip_id)

            # Create trip_id to route_id mapping from trips.txt
            trip_to_route = {}
            with open(trips_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    trip_to_route[row['trip_id']] = row['route_id']

            # Create stop_id to route_id mapping
            station_route_map = {}
            for stop_id, trips in stop_to_trips.items():
                route_ids = set()
                for trip_id in trips:
                    if trip_id in trip_to_route:
                        route_ids.add(trip_to_route[trip_id])
                station_route_map[stop_id] = list(route_ids)

            # Cache the result
            cache.set(cache_key, station_route_map)
            return station_route_map

        except Exception as e:
            return {"error": f"Failed to create station-route map: {str(e)}"}

    def get_routes_for_station(self, station_id):
        """
        Get all routes serving a specific station with details

        Args:
            station_id (str): Station ID

        Returns:
            dict: Routes information for the station
        """
        # Get station-route mapping
        mapping = self.get_station_route_map()
        if "error" in mapping:
            return mapping

        if station_id not in mapping:
            return {"error": "Station not found"}

        route_ids = mapping[station_id]

        # Get route details
        routes = []
        routes_file = os.path.join('data', 'gtfs_subway', 'routes.txt')

        try:
            with open(routes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['route_id'] in route_ids:
                        route = {
                            "id": row['route_id'],
                            "short_name": row['route_short_name'],
                            "long_name": row['route_long_name'],
                            "color": row.get('route_color', ''),
                            "text_color": row.get('route_text_color', '')
                        }
                        routes.append(route)

            return {
                "station_id": station_id,
                "routes": routes
            }

        except Exception as e:
            return {"error": f"Failed to get routes for station: {str(e)}"}


    def get_stops_for_route(self, route_id):
        """
        Get all stops for a specific route

        Args:
            route_id (str): Route ID

        Returns:
            list: List of stops for the route
        """
        # Check cache
        cache_key = f"route_stops_{route_id}"
        cached_data = cache.get(cache_key, self.get_cache_timeout('route_stops', route_id))
        if cached_data:
            return cached_data

        try:
            # file addr
            trips_file = os.path.join('data', 'gtfs_subway', 'trips.txt')
            stop_times_file = os.path.join('data', 'gtfs_subway', 'stop_times.txt')
            stops_file = os.path.join('data', 'gtfs_subway', 'stops.txt')

            #  route trip
            representative_trip_id = None
            with open(trips_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['route_id'] == route_id:

                        if 'direction_id' in row and row['direction_id'] == '0':
                            representative_trip_id = row['trip_id']
                            break

                        if not representative_trip_id:
                            representative_trip_id = row['trip_id']

            if not representative_trip_id:
                return {"error": f"No trips found for route: {route_id}"}

            #  stop_sequence
            stop_sequence = []
            with open(stop_times_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['trip_id'] == representative_trip_id:
                        stop_sequence.append({
                            'stop_id': row['stop_id'],
                            'sequence': int(row['stop_sequence'])
                        })

            stop_sequence.sort(key=lambda x: x['sequence'])

            stops_info = {}
            with open(stops_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stops_info[row['stop_id']] = {
                        "id": row['stop_id'],
                        "name": row['stop_name'],
                        "lat": float(row['stop_lat']),
                        "lng": float(row['stop_lon'])
                    }

            # ordered_list
            ordered_stops = []
            for stop in stop_sequence:
                if stop['stop_id'] in stops_info:
                    ordered_stops.append(stops_info[stop['stop_id']])

            result = {
                "route_id": route_id,
                "stops": ordered_stops
            }

            cache.set(cache_key, result)
            return result

        except Exception as e:
            return {"error": f"Failed to load stops for route: {str(e)}"}

    def get_station_details(self, station_id):
        """
        Get comprehensive station details including accessibility info, routes, and schedule
        """
        cache_key = f"station_details_{station_id}"
        cached_data = cache.get(cache_key, 300)  # cache 5 min
        if cached_data:
            return cached_data

        try:

            stops_file = os.path.join('data', 'gtfs_subway', 'stops.txt')
            station_info = None

            with open(stops_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['stop_id'] == station_id:
                        station_info = {
                            "id": row['stop_id'],
                            "name": row['stop_name'],
                            "lat": float(row['stop_lat']),
                            "lng": float(row['stop_lon']),
                            "wheelchair_boarding": row.get('wheelchair_boarding', '0'),
                            "location_type": row.get('location_type', '0')
                        }
                        break

            if not station_info:
                return {"error": "Station not found"}


            routes_data = self.get_routes_for_station(station_id)
            station_info["routes"] = routes_data.get("routes", []) if "error" not in routes_data else []


            equipment_data = self.get_accessibility_data('equipment')
            current_outages = self.get_accessibility_data('current')


            accessibility_info = {
                "has_accessibility": False,
                "equipment": []
            }

            if not isinstance(equipment_data, dict) or "error" not in equipment_data:
                station_name = station_info["name"].strip()
                matching_equipment = []


                cleaned_station_name = station_name.lower()

                for item in equipment_data:
                    item_station = item.get('station', '').strip().lower()
                    gtfs_id = item.get('elevatorgtfsstopid', '')

                    # mach :GTFS ID or station name
                    if gtfs_id == station_id or (item_station and (
                            item_station in cleaned_station_name or
                            cleaned_station_name in item_station)):

                        equipment_info = {
                            'equipment_no': item.get('equipmentno', ''),
                            'equipment_type': item.get('equipmenttype', ''),
                            'serving': item.get('serving', ''),
                            'is_active': item.get('isactive', '') != 'Y'
                        }

                        if not isinstance(current_outages, dict) or "error" not in current_outages:
                            equipment_id = item.get('equipmentno', '')
                            if "outages" in current_outages:
                                for outage in current_outages["outages"]:
                                    if outage.get("equipment_id") == equipment_id:
                                        equipment_info["current_status"] = outage

                        matching_equipment.append(equipment_info)


                if matching_equipment:
                    accessibility_info["has_accessibility"] = True
                    accessibility_info["equipment"] = matching_equipment

            station_info["accessibility"] = accessibility_info

            schedule_info = self.get_station_schedule(station_id)
            station_info["schedule"] = schedule_info

            cache.set(cache_key, station_info)
            return station_info

        except Exception as e:
            import traceback
            trace = traceback.format_exc()
            return {"error": f"Failed to get station details: {str(e)}", "trace": trace}

    def get_station_schedule(self, station_id):
        """
        Get schedule information for a station, including all routes serving it

        Args:
            station_id (str): Station ID

        Returns:
            dict: Schedule information
        """
        try:

            stop_times_file = os.path.join('data', 'gtfs_subway', 'stop_times.txt')
            trips_file = os.path.join('data', 'gtfs_subway', 'trips.txt')

            routes_for_station = self.get_routes_for_station(station_id)
            route_ids = [route["id"] for route in routes_for_station.get("routes", [])]

            # get route id
            trip_ids_by_route = {}
            with open(trips_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['route_id'] in route_ids:
                        if row['route_id'] not in trip_ids_by_route:
                            trip_ids_by_route[row['route_id']] = []
                        trip_ids_by_route[row['route_id']].append(row['trip_id'])

            # get trip id
            all_trip_ids = [trip_id for trips in trip_ids_by_route.values() for trip_id in trips]

            trip_info = {}
            with open(trips_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['trip_id'] in all_trip_ids:
                        trip_info[row['trip_id']] = {
                            'route_id': row['route_id'],
                            'service_id': row['service_id'],
                            'trip_headsign': row.get('trip_headsign', ''),
                            'direction_id': row.get('direction_id', ''),
                            'trip_id': row['trip_id']
                        }

            # get time
            current_time = datetime.datetime.now().time()
            current_time_str = current_time.strftime('%H:%M:%S')


            future_stop_times = []
            with open(stop_times_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['stop_id'] == station_id and row['trip_id'] in all_trip_ids:
                        if row['arrival_time'] > current_time_str:
                            future_stop_times.append({
                                'trip_id': row['trip_id'],
                                'arrival_time': row['arrival_time'],
                                'departure_time': row['departure_time'],
                                'stop_sequence': int(row['stop_sequence'])
                            })

            # sorted by time
            future_stop_times.sort(key=lambda x: x['arrival_time'])

            # each line can only get 5 future trip
            max_trips_per_route = 5
            route_trip_count = {}
            filtered_stop_times = []

            for time in future_stop_times:
                trip_id = time['trip_id']
                if trip_id in trip_info:
                    route_id = trip_info[trip_id]['route_id']

                    if route_id not in route_trip_count:
                        route_trip_count[route_id] = 0

                    if route_trip_count[route_id] < max_trips_per_route:
                        filtered_stop_times.append(time)
                        route_trip_count[route_id] += 1

            schedule = []
            for time in filtered_stop_times:
                if time['trip_id'] in trip_info:
                    trip = trip_info[time['trip_id']]
                    schedule.append({
                        'route_id': trip['route_id'],
                        'trip_headsign': trip['trip_headsign'],
                        'arrival_time': time['arrival_time'],
                        'departure_time': time['departure_time'],
                        'direction_id': trip['direction_id']
                    })

            # max schedule limit
            max_schedule_entries = 40
            if len(schedule) > max_schedule_entries:
                schedule = schedule[:max_schedule_entries]

            return {
                'schedule_entries': len(schedule),
                'schedule': schedule
            }

        except Exception as e:
            return {"error": f"Failed to get station schedule: {str(e)}"}

    def get_accessibility_data(self, data_type):
        """
        Get accessibility data

        Args:
            data_type (str): Data type ('current', 'upcoming', 'equipment')

        Returns:
            dict: Accessibility data or error
        """

        if data_type not in ELEVATOR_ESCALATOR_FEEDS:
            return {"error": f"Invalid accessibility data type: {data_type}"}


        cache_key = f"accessibility_{data_type}"
        cached_data = cache.get(cache_key, self.get_cache_timeout('accessibility', data_type))
        if cached_data:
            return cached_data


        try:
            response = requests.get(ELEVATOR_ESCALATOR_FEEDS[data_type])

            if response.status_code == 200:
                data = response.json()

                cache.set(cache_key, data)
                return data
            else:
                return {"error": f"HTTP error: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def get_station_route_schedule(self, station_id, route_id):
        """
        Get schedule for a specific route at a specific station

        Args:
            station_id (str): Station ID
            route_id (str): Route ID

        Returns:
            dict: Schedule information for specific route
        """
        try:

            stop_times_file = os.path.join('data', 'gtfs_subway', 'stop_times.txt')
            trips_file = os.path.join('data', 'gtfs_subway', 'trips.txt')

            trip_ids = []
            with open(trips_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['route_id'] == route_id:
                        trip_ids.append(row['trip_id'])

            if not trip_ids:
                return {"error": f"No trips found for route {route_id}"}


            trip_info = {}
            with open(trips_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['trip_id'] in trip_ids:
                        trip_info[row['trip_id']] = {
                            'trip_headsign': row.get('trip_headsign', ''),
                            'direction_id': row.get('direction_id', '')
                        }


            current_time = datetime.datetime.now().time()
            current_time_str = current_time.strftime('%H:%M:%S')


            future_stop_times = []
            with open(stop_times_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['stop_id'] == station_id and row['trip_id'] in trip_ids:

                        if row['arrival_time'] > current_time_str:
                            future_stop_times.append({
                                'trip_id': row['trip_id'],
                                'arrival_time': row['arrival_time'],
                                'departure_time': row['departure_time']
                            })


            future_stop_times.sort(key=lambda x: x['arrival_time'])


            max_schedule_entries = 10
            if len(future_stop_times) > max_schedule_entries:
                future_stop_times = future_stop_times[:max_schedule_entries]


            schedule = []
            for time in future_stop_times:
                if time['trip_id'] in trip_info:
                    trip = trip_info[time['trip_id']]
                    schedule.append({
                        'trip_headsign': trip['trip_headsign'],
                        'arrival_time': time['arrival_time'],
                        'departure_time': time['departure_time'],
                        'direction_id': trip['direction_id']
                    })

            return {
                'station_id': station_id,
                'route_id': route_id,
                'schedule_entries': len(schedule),
                'schedule': schedule
            }

        except Exception as e:
            return {"error": f"Failed to get station route schedule: {str(e)}"}

    def get_accessible_stations(self):
        """
        Get all stations with accessibility features based on MTA's accessibility API
        """
        try:

            cache_key = "accessible_stations"
            cached_data = None  # 测试时临时禁用缓存
            if cached_data:
                return cached_data


            equipment_data = self.get_accessibility_data('equipment')
            if "error" in equipment_data:
                return {"error": f"Failed to get equipment data: {equipment_data['error']}"}

            print(f"Equipment data count: {len(equipment_data) if isinstance(equipment_data, list) else 'not a list'}")


            station_route_map = self.get_station_route_map()
            if isinstance(station_route_map, dict) and "error" in station_route_map:
                print(f"Error getting station route map: {station_route_map['error']}")
                station_route_map = {}
            else:
                print(f"Station route map keys: {len(station_route_map)} entries")
                sample_keys = list(station_route_map.keys())[:5]
                print(f"Sample station IDs in route map: {sample_keys}")
                for key in sample_keys:
                    print(f"  Routes for {key}: {station_route_map[key]}")


            all_routes = {}
            routes_file = os.path.join('data', 'gtfs_subway', 'routes.txt')
            try:
                with open(routes_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        all_routes[row['route_id']] = {
                            "id": row['route_id'],
                            "short_name": row['route_short_name'],
                            "long_name": row['route_long_name'],
                            "color": row.get('route_color', ''),
                            "text_color": row.get('route_text_color', '')
                        }
                print(f"Total routes loaded: {len(all_routes)}")
            except Exception as e:
                print(f"Error reading routes file: {str(e)}")
                all_routes = {}


            stations_by_complex = {}


            for item in equipment_data:
                complex_id = item.get('stationcomplexid', '').strip()
                gtfs_id = item.get('elevatorgtfsstopid', '').strip()
                station_name = item.get('station', '').strip()

                if not complex_id or not station_name:
                    continue

                if complex_id not in stations_by_complex:
                    stations_by_complex[complex_id] = {
                        'id': complex_id,
                        'name': station_name,
                        'has_accessibility': True,
                        'equipment': [],
                        'routes': [],
                        'gtfs_ids': set()
                    }


                equipment_info = {
                    'equipment_no': item.get('equipmentno', ''),
                    'equipment_type': item.get('equipmenttype', ''),
                    'serving': item.get('serving', ''),
                    'is_active': item.get('isactive', '') != 'Y'
                }
                stations_by_complex[complex_id]['equipment'].append(equipment_info)


                if gtfs_id:
                    stations_by_complex[complex_id]['gtfs_ids'].add(gtfs_id)


            for complex_id, station_data in stations_by_complex.items():
                gtfs_ids = station_data['gtfs_ids']
                print(f"Processing station {station_data['name']} with GTFS IDs: {gtfs_ids}")

                route_ids = set()


                for gtfs_id in gtfs_ids:
                    if gtfs_id in station_route_map:
                        found_routes = station_route_map[gtfs_id]
                        print(f"  Found routes {found_routes} for GTFS ID {gtfs_id}")
                        route_ids.update(found_routes)


                for route_id in route_ids:
                    if route_id in all_routes:
                        station_data['routes'].append(all_routes[route_id])

                print(f"  Final routes count: {len(station_data['routes'])}")

                station_data['gtfs_ids'] = list(station_data['gtfs_ids'])


            accessible_stations = []
            for station in stations_by_complex.values():
                if 'gtfs_ids' in station:
                    del station['gtfs_ids']
                accessible_stations.append(station)

            print(f"\nTotal accessible stations: {len(accessible_stations)}")


            cache.set(cache_key, accessible_stations)
            return accessible_stations

        except Exception as e:
            import traceback
            trace = traceback.format_exc()
            print(f"Error in get_accessible_stations: {str(e)}")
            print(trace)
            return {"error": f"Failed to get accessible stations: {str(e)}", "trace": trace}

