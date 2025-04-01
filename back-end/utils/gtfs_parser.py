from google.transit import gtfs_realtime_pb2
import time
import datetime


def parse_gtfs_rt(content, feed_id):
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
                    "timestamp": vehicle.timestamp,
                    "human_time": datetime.datetime.fromtimestamp(vehicle.timestamp).strftime(
                        '%Y-%m-%d %H:%M:%S') if vehicle.timestamp else None
                }

                if vehicle.HasField('position'):
                    vehicle_data["position"] = {
                        "latitude": vehicle.position.latitude,
                        "longitude": vehicle.position.longitude,
                        "bearing": vehicle.position.bearing if vehicle.position.HasField('bearing') else None,
                        "speed": vehicle.position.speed if vehicle.position.HasField('speed') else None
                    }

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
                    "timestamp": trip_update.timestamp,
                    "human_time": datetime.datetime.fromtimestamp(trip_update.timestamp).strftime(
                        '%Y-%m-%d %H:%M:%S') if trip_update.timestamp else None,
                    "stop_time_updates": []
                }

                for stop_time in trip_update.stop_time_update:
                    stop_data = {"stop_id": stop_time.stop_id}

                    if stop_time.HasField('arrival'):
                        arrival_time = datetime.datetime.fromtimestamp(
                            stop_time.arrival.time) if stop_time.arrival.time else None
                        stop_data["arrival"] = {
                            "time": stop_time.arrival.time,
                            "human_time": arrival_time.strftime('%Y-%m-%d %H:%M:%S') if arrival_time else None,
                            "delay": stop_time.arrival.delay if stop_time.arrival.HasField('delay') else None
                        }

                    if stop_time.HasField('departure'):
                        departure_time = datetime.datetime.fromtimestamp(
                            stop_time.departure.time) if stop_time.departure.time else None
                        stop_data["departure"] = {
                            "time": stop_time.departure.time,
                            "human_time": departure_time.strftime('%Y-%m-%d %H:%M:%S') if departure_time else None,
                            "delay": stop_time.departure.delay if stop_time.departure.HasField('delay') else None
                        }

                    update_data["stop_time_updates"].append(stop_data)

                entity_data["trip_update"] = update_data

            # Process alerts
            if entity.HasField('alert'):
                alert = entity.alert
                alert_data = {
                    "active_period": [],
                    "informed_entity": [],
                    "cause": alert.cause,
                    "effect": alert.effect,
                    "url": alert.url.translation[0].text if alert.url.translation else None,
                    "header_text": alert.header_text.translation[0].text if alert.header_text.translation else None,
                    "description_text": alert.description_text.translation[
                        0].text if alert.description_text.translation else None
                }

                # Process active periods
                for period in alert.active_period:
                    period_data = {}
                    if period.HasField('start'):
                        start_time = datetime.datetime.fromtimestamp(period.start)
                        period_data["start"] = {
                            "timestamp": period.start,
                            "human_time": start_time.strftime('%Y-%m-%d %H:%M:%S')
                        }

                    if period.HasField('end'):
                        end_time = datetime.datetime.fromtimestamp(period.end)
                        period_data["end"] = {
                            "timestamp": period.end,
                            "human_time": end_time.strftime('%Y-%m-%d %H:%M:%S')
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