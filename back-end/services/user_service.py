from models import db, User, FavoriteRoute, FavoriteStation, NotificationSetting
from werkzeug.security import generate_password_hash, check_password_hash


class UserService:
    """User-related services"""

    def create_user(self, username, email, password):
        """Create a new user"""
        # Check if username or email already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return None, "Username or email already exists"

        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        return user, None

    def add_favorite_route(self, user_id, route_id):
        """Add a favorite route"""
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"

        # Check if route is already favorited
        existing = (FavoriteRoute.query.
                    filter_by(user_id=user_id, route_id=route_id).first())
        if existing:
            return existing, "Route already favorited"

        # Add new favorite
        favorite = FavoriteRoute(user_id=user_id, route_id=route_id)
        db.session.add(favorite)
        db.session.commit()

        return favorite, None

    def get_user_favorite_routes(self, user_id):
        """Get user's favorite routes"""
        return FavoriteRoute.query.filter_by(user_id=user_id).all()

