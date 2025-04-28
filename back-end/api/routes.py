import csv
import os

from flask import jsonify, request
from services.data_service import DataService
from services.user_service import UserService
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from utils.firebase_middleware import firebase_auth_required
from models import User, FavoriteRoute, FavoriteStation, NotificationSetting, db
from datetime import datetime


def register_routes(bp):
    # Initialize service
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


        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            return jsonify({"access_token": access_token})

        return jsonify({"error": "Invalid credentials"}), 401

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

    @bp.route('/stations/accessible')
    def get_accessible_stations():
        """Get all stations with accessibility features"""
        stations = data_service.get_accessible_stations()
        return jsonify(stations)

    @bp.route('/test/accessibility/equipment')
    def test_accessibility_equipment():
        """Test endpoint to check equipment data from MTA API"""
        equipment_data = data_service.get_accessibility_data('equipment')
        return jsonify(equipment_data)

    @bp.route('/debug/gtfs-mapping-issue')
    def investigate_gtfs_mapping():
        """调查GTFS映射问题"""
        data = data_service.investigate_gtfs_mapping_issue()
        return jsonify(data)

    @bp.route('/users/sync', methods=['POST'])
    @firebase_auth_required()
    def sync_user():
        """sync Firebase to database"""
        user = request.current_user
        return jsonify({
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        })

    # 收藏路线相关路由
    @bp.route('/users/favorites/routes', methods=['GET'])
    @firebase_auth_required()
    def get_favorite_routes():
        """get users favorites routes"""
        user = request.current_user
        favorites = FavoriteRoute.query.filter_by(user_id=user.id).all()

        return jsonify([{
            'id': fav.id,
            'route_id': fav.route_id,
            'added_at': fav.added_at.isoformat()
        } for fav in favorites])

    @bp.route('/users/favorites/routes', methods=['POST'])
    @firebase_auth_required()
    def add_favorite_route():
        """add favorite routes"""
        user = request.current_user
        data = request.json

        if not data or 'route_id' not in data:
            return jsonify({'error': 'Route ID is required'}), 400

        # 检查是否已收藏
        existing = FavoriteRoute.query.filter_by(
            user_id=user.id,
            route_id=data['route_id']
        ).first()

        if existing:
            return jsonify({'error': 'Route already favorited'}), 400

        favorite = FavoriteRoute(
            user_id=user.id,
            route_id=data['route_id']
        )
        db.session.add(favorite)
        db.session.commit()

        return jsonify({
            'message': 'Route added to favorites',
            'id': favorite.id
        }), 201

    @bp.route('/users/favorites/routes/<int:favorite_id>', methods=['DELETE'])
    @firebase_auth_required()
    def remove_favorite_route(favorite_id):
        """delete favorite route"""
        user = request.current_user
        favorite = FavoriteRoute.query.filter_by(
            id=favorite_id,
            user_id=user.id
        ).first()

        if not favorite:
            return jsonify({'error': 'Favorite not found'}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({'message': 'Favorite removed'})

    # favorites api
    @bp.route('/users/favorites/stations', methods=['GET'])
    @firebase_auth_required()
    def get_favorite_stations():
        """get favorite stations"""
        user = request.current_user
        favorites = FavoriteStation.query.filter_by(user_id=user.id).all()

        return jsonify([{
            'id': fav.id,
            'station_id': fav.station_id,
            'added_at': fav.added_at.isoformat()
        } for fav in favorites])

    @bp.route('/users/favorites/stations', methods=['POST'])
    @firebase_auth_required()
    def add_favorite_station():
        """add favorite stations"""
        user = request.current_user
        data = request.json

        if not data or 'station_id' not in data:
            return jsonify({'error': 'Station ID is required'}), 400

        existing = FavoriteStation.query.filter_by(
            user_id=user.id,
            station_id=data['station_id']
        ).first()

        if existing:
            return jsonify({'error': 'Station already favorited'}), 400

        favorite = FavoriteStation(
            user_id=user.id,
            station_id=data['station_id']
        )
        db.session.add(favorite)
        db.session.commit()

        return jsonify({
            'message': 'Station added to favorites',
            'id': favorite.id
        }), 201

    @bp.route('/users/favorites/stations/<int:favorite_id>', methods=['DELETE'])
    @firebase_auth_required()
    def remove_favorite_station(favorite_id):
        """delete favorite stations"""
        user = request.current_user
        favorite = FavoriteStation.query.filter_by(
            id=favorite_id,
            user_id=user.id
        ).first()

        if not favorite:
            return jsonify({'error': 'Favorite not found'}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({'message': 'Favorite removed'})

    # notification api
    @bp.route('/users/notifications', methods=['GET'])
    @firebase_auth_required()
    def get_notification_settings():
        """get user notifications"""
        user = request.current_user
        settings = NotificationSetting.query.filter_by(user_id=user.id).all()

        return jsonify([{
            'id': setting.id,
            'notification_type': setting.notification_type,
            'route_id': setting.route_id,
            'station_id': setting.station_id,
            'is_enabled': setting.is_enabled,
            'updated_at': setting.updated_at.isoformat()
        } for setting in settings])

    @bp.route('/users/notifications', methods=['POST'])
    @firebase_auth_required()
    def update_notification_settings():
        """update user notifications"""
        user = request.current_user
        data = request.json

        if not data or 'notification_type' not in data:
            return jsonify({'error': 'Notification type is required'}), 400

        # 查找现有设置
        existing = NotificationSetting.query.filter_by(
            user_id=user.id,
            notification_type=data['notification_type'],
            route_id=data.get('route_id'),
            station_id=data.get('station_id')
        ).first()

        if existing:
            # 更新现有设置
            existing.is_enabled = data.get('is_enabled', True)
            existing.updated_at = datetime.utcnow()
        else:
            # 创建新设置
            existing = NotificationSetting(
                user_id=user.id,
                notification_type=data['notification_type'],
                route_id=data.get('route_id'),
                station_id=data.get('station_id'),
                is_enabled=data.get('is_enabled', True)
            )
            db.session.add(existing)

        db.session.commit()

        return jsonify({
            'message': 'Notification settings updated',
            'id': existing.id
        })

    @bp.route('/users/notifications/<int:setting_id>', methods=['DELETE'])
    @firebase_auth_required()
    def delete_notification_setting(setting_id):
        """delete user notifications"""
        user = request.current_user
        setting = NotificationSetting.query.filter_by(
            id=setting_id,
            user_id=user.id
        ).first()

        if not setting:
            return jsonify({'error': 'Notification setting not found'}), 404

        db.session.delete(setting)
        db.session.commit()

        return jsonify({'message': 'Notification setting deleted'})