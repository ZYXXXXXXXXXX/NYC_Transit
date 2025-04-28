# utils/firebase_middleware.py
from firebase_admin import auth
from functools import wraps
from flask import request, jsonify
from datetime import datetime


def firebase_auth_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("\n=== Firebase Auth Middleware Debug ===")
            auth_header = request.headers.get('Authorization')
            print(f"Authorization header present: {bool(auth_header)}")

            if not auth_header:
                print("Error: No Authorization header")
                return jsonify({'error': 'No token provided'}), 401

            if not auth_header.startswith('Bearer '):
                print("Error: Authorization header doesn't start with 'Bearer '")
                return jsonify({'error': 'Invalid token format'}), 401

            id_token = auth_header.split(' ')[1]
            print(f"Token extracted, length: {len(id_token)}")

            try:
                print("Attempting to verify token...")
                decoded_token = auth.verify_id_token(id_token)
                print(f"Token verified successfully for UID: {decoded_token.get('uid')}")

                from models import User, db

                # 查找或创建本地用户
                user = User.query.filter_by(firebase_uid=decoded_token['uid']).first()

                if not user:
                    print(f"Creating new user for UID: {decoded_token['uid']}")
                    user = User(
                        firebase_uid=decoded_token['uid'],
                        email=decoded_token.get('email', ''),
                        username=decoded_token.get('name') or decoded_token.get('email', '').split('@')[0]
                    )
                    db.session.add(user)
                    db.session.commit()
                    print(f"New user created with ID: {user.id}")
                else:
                    print(f"Existing user found: {user.email}")

                # 更新最后登录时间
                user.last_login = datetime.utcnow()
                db.session.commit()
                print(f"Updated last login for user: {user.id}")

                # 用户信息添加到request
                request.current_user = user
                print("User attached to request context")

            except Exception as e:
                print(f"Token verification failed: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return jsonify({'error': 'Invalid token', 'details': str(e)}), 401

            print("Firebase auth middleware completed successfully\n")
            return f(*args, **kwargs)

        return decorated_function

    return decorator