import firebase_admin
from firebase_admin import credentials, auth

# 初始化 Firebase Admin SDK
cred = credentials.Certificate('path/to/your-firebase-adminsdk.json')
firebase_app = firebase_admin.initialize_app(cred)