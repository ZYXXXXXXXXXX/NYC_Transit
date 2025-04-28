# test_firebase_integration.py
from firebase_admin import auth
from firebase_config import firebase_app  # 确保已初始化Firebase
import time


def test_firebase_token_validation():
    """测试Firebase token验证"""
    # 需要一个有效的Firebase ID token来测试
    # 可以从前端登录获取
    test_token = input("请输入Firebase ID Token进行测试: ")

    try:
        decoded_token = auth.verify_id_token(test_token)
        print("Token验证成功！")
        print(f"用户UID: {decoded_token['uid']}")
        print(f"用户邮箱: {decoded_token.get('email', 'N/A')}")
        return True
    except Exception as e:
        print(f"Token验证失败: {e}")
        return False


if __name__ == "__main__":
    test_firebase_token_validation()