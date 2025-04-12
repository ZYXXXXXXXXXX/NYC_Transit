from flask import jsonify, request
from services.data_service import DataService
from flask import jsonify, request

from services.user_service import UserService
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

def register_routes(bp):

   # Initialize  service
   data_service = DataService()
   user_service = UserService()

   @bp.route('/feeds')
   def list_feeds():
       """List all available data feeds"""
       feeds = data_service.get_available_feeds()
       return jsonify(feeds)

   @bp.route('/health')
   def health_check():
       """Health check endpoint"""
       return jsonify({"status": "ok", "message": "Service is running"})

   # Subway endpoints
   @bp.route('/subway/feeds')
   def list_subway_feeds():
       """List all available subway feeds"""
       return jsonify(data_service.get_subway_feeds())

   @bp.route('/subway/feeds/<feed_id>')
   def get_subway_feed(feed_id):
       """Get data for specific subway feed"""
       data = data_service.get_subway_feed(feed_id)
       return jsonify(data)

   # LIRR endpoints
   @bp.route('/lirr/feeds/<feed_id>')
   def get_lirr_feed(feed_id):
       """Get LIRR data"""
       data = data_service.get_lirr_feed(feed_id)
       return jsonify(data)

   # Metro-North endpoints
   @bp.route('/mnr/feeds/<feed_id>')
   def get_mnr_feed(feed_id):
       """Get Metro-North data"""
       data = data_service.get_mnr_feed(feed_id)
       return jsonify(data)

   # Service alert endpoints
   @bp.route('/alerts/<alert_type>')
   def get_service_alerts(alert_type):
       """Get service alerts"""
       data = data_service.get_service_alerts(alert_type)
       return jsonify(data)

   # Accessibility endpoints
   @bp.route('/accessibility/<data_type>')
   def get_accessibility_data(data_type):
       """Get accessibility data"""
       data = data_service.get_accessibility_data(data_type)
       return jsonify(data)

   @bp.route('/accessibility/station/<station_id>')
   def get_station_accessibility(station_id):
       """Get station accessibility info"""
       data = data_service.get_station_accessibility(station_id)
       return jsonify(data)

   @bp.route('/stations')
   def list_stations():
       """List all stations"""
       stations = data_service.get_stations()
       return jsonify(stations)

   @bp.route('/routes')
   def list_routes():
       """List all routes"""
       routes = data_service.get_routes()
       return jsonify(routes)

   @bp.route('/routes/<route_id>/shape')
   def get_route_shape(route_id):
       """Get shape for a specific route"""
       shape_data = data_service.get_line_shape(route_id)
       return jsonify(shape_data)

   @bp.route('/routes/<route_id>/stops')
   def get_route_stops(route_id):
       """Get stops for a specific route"""
       stops_data = data_service.get_stops_for_route(route_id)
       return jsonify(stops_data)

   @bp.route('/line/<line_id>')
   def get_line(line_id):
       """Get line coordinates"""
       line_data = data_service.get_line(line_id)
       return jsonify(line_data)

   # user_service
   @bp.route('/users/register', methods=['POST'])
   def register_user():
       """Register a new user"""
       data = request.json
       if not data or not all(k in data for k in ('username', 'email', 'password')):
           return jsonify({"error": "Please provide username, email, and password"}), 400

       user, error = user_service.create_user(data['username'], data['email'], data['password'])
       if error:
           return jsonify({"error": error}), 400

       return jsonify({"message": "User registered successfully", "user_id": user.id}), 201

   @bp.route('/users/login', methods=['POST'])
   def login():
       """User login"""
       data = request.json
       if not data or not all(k in data for k in ('username', 'password')):
           return jsonify({"error": "Please provide username and password"}), 400

       # Implement login logic
       # Return JWT token
       pass

   @bp.route('/users/<int:user_id>/favorites/routes', methods=['GET'])

   def get_favorite_routes(user_id):
       """Get user's favorite routes"""
       # Verify identity
       current_user = get_jwt_identity()
       if current_user != user_id:
           return jsonify({"error": "Unauthorized access"}), 403

       favorites = user_service.get_user_favorite_routes(user_id)
       return jsonify([{
           "id": fav.id,
           "route_id": fav.route_id,
           "added_at": fav.added_at.isoformat()
       } for fav in favorites])

   @bp.route('/users/<int:user_id>/favorites/routes', methods=['POST'])

   def add_favorite_route(user_id):
       """Add a favorite route"""
       # Implement add favorite logic
       pass

   @bp.route('/station-route-map')
   def get_station_route_map():
       """Get mapping between stations and routes"""
       mapping = data_service.get_station_route_map()
       if "error" in mapping:
           return jsonify(mapping), 500
       return jsonify(mapping)

   @bp.route('/stations/<station_id>/routes')
   def get_routes_for_station(station_id):
       """Get all routes serving a specific station"""
       result = data_service.get_routes_for_station(station_id)
       if "error" in result:
           error_message = result["error"]
           if error_message == "Station not found":
               return jsonify(result), 404
           return jsonify(result), 500
       return jsonify(result)

   @bp.route('/stations/<station_id>/details')
   def get_station_details(station_id):
       """Get comprehensive station details"""
       details = data_service.get_station_details(station_id)
       if "error" in details:
           error_message = details["error"]
           if error_message == "Station not found":
               return jsonify(details), 404
           return jsonify(details), 500
       return jsonify(details)

   @bp.route('/stations/<station_id>/routes/<route_id>/schedule')
   def get_station_route_schedule(station_id, route_id):
       """Get schedule for a specific route at a specific station"""
       data = data_service.get_station_route_schedule(station_id, route_id)
       return jsonify(data)