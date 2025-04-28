# firebase_config.py
import firebase_admin
from firebase_admin import credentials, auth
import os

#保证数据库在项目文件夹生成
if not firebase_admin._apps:

    cred_path = os.path.join(os.path.dirname(__file__), '..', 'path/to/your-firebase-adminsdk.json')

    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Firebase credentials not found at {cred_path}")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    print("Firebase initialized successfully")