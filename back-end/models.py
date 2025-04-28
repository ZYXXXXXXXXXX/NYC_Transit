from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 初始化SQLAlchemy实例
db = SQLAlchemy()


# models.py --添加了firebase uid
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)  # 添加Firebase UID
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # 关系
    favorite_routes = db.relationship('FavoriteRoute', backref='user', lazy=True)
    favorite_stations = db.relationship('FavoriteStation', backref='user', lazy=True)
    notification_settings = db.relationship('NotificationSetting', backref='user', lazy=True)


class FavoriteRoute(db.Model):
    """User's favorite routes"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    route_id = db.Column(db.String(20), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)


class FavoriteStation(db.Model):
    """User's favorite stations"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    station_id = db.Column(db.String(20), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)


class NotificationSetting(db.Model):
    """User notification settings"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_type = db.Column(db.String(20), nullable=False)  # delay, service_change, etc.
    route_id = db.Column(db.String(20), nullable=True)  # Can be null for global settings
    station_id = db.Column(db.String(20), nullable=True)  # Can be null
    is_enabled = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)