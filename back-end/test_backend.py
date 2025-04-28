# test_backend.py
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"


class BackendTester:
    def __init__(self):
        self.firebase_token = None
        self.user_id = None

    def test_health_check(self):
        """测试健康检查端点"""
        print("\n=== 测试健康检查 ===")
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200

    def test_stations_endpoint(self):
        """测试站点数据端点"""
        print("\n=== 测试站点数据 ===")
        response = requests.get(f"{BASE_URL}/subway/stations")
        print(f"状态码: {response.status_code}")
        stations = response.json()
        print(f"获取到 {len(stations)} 个站点")
        if stations:
            print(f"示例站点: {stations[0]}")
        return response.status_code == 200

    def test_routes_endpoint(self):
        """测试线路数据端点"""
        print("\n=== 测试线路数据 ===")
        response = requests.get(f"{BASE_URL}/subway/routes")
        print(f"状态码: {response.status_code}")
        routes = response.json()
        print(f"获取到 {len(routes)} 条线路")
        if routes:
            print(f"示例线路: {routes[0]}")
        return response.status_code == 200

    def test_firebase_auth(self, firebase_token):
        """测试Firebase认证"""
        print("\n=== 测试Firebase认证 ===")
        self.firebase_token = firebase_token
        headers = {"Authorization": f"Bearer {firebase_token}"}

        # 测试用户同步
        response = requests.post(f"{BASE_URL}/users/sync", headers=headers)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            user_data = response.json()
            print(f"用户数据: {user_data}")
            self.user_id = user_data.get('user_id')
            return True
        else:
            print(f"错误: {response.json()}")
            return False

    def test_favorites(self):
        """测试收藏功能"""
        if not self.firebase_token or not self.user_id:
            print("请先运行 test_firebase_auth")
            return False

        print("\n=== 测试收藏功能 ===")
        headers = {"Authorization": f"Bearer {self.firebase_token}"}

        # 添加收藏路线
        data = {"route_id": "A"}
        response = requests.post(
            f"{BASE_URL}/users/favorites/routes",
            headers=headers,
            json=data
        )
        print(f"添加收藏状态码: {response.status_code}")
        print(f"添加收藏响应: {response.json()}")

        # 获取收藏列表
        response = requests.get(
            f"{BASE_URL}/users/favorites/routes",
            headers=headers
        )
        print(f"获取收藏状态码: {response.status_code}")
        print(f"收藏列表: {response.json()}")

        return response.status_code == 200

    def test_notifications(self):
        """测试通知设置"""
        if not self.firebase_token or not self.user_id:
            print("请先运行 test_firebase_auth")
            return False

        print("\n=== 测试通知设置 ===")
        headers = {"Authorization": f"Bearer {self.firebase_token}"}

        # 设置通知
        data = {
            "notification_type": "delay",
            "route_id": "A",
            "is_enabled": True
        }
        response = requests.post(
            f"{BASE_URL}/users/notifications",
            headers=headers,
            json=data
        )
        print(f"设置通知状态码: {response.status_code}")
        print(f"设置通知响应: {response.json()}")

        # 获取通知设置
        response = requests.get(
            f"{BASE_URL}/users/notifications",
            headers=headers
        )
        print(f"获取通知设置状态码: {response.status_code}")
        print(f"通知设置列表: {response.json()}")

        return response.status_code == 200


def run_all_tests():
    tester = BackendTester()

    # 运行基础测试
    tester.test_health_check()
    tester.test_stations_endpoint()
    tester.test_routes_endpoint()

    # 如果有Firebase Token，运行认证测试
    # 从Firebase前端获取有效的ID token
    firebase_token = input("\n请输入Firebase ID Token (直接回车跳过认证测试): ")

    if firebase_token:
        if tester.test_firebase_auth(firebase_token):
            tester.test_favorites()
            tester.test_notifications()
    else:
        print("\n跳过认证测试")

    print("\n测试完成！")


if __name__ == "__main__":
    run_all_tests()