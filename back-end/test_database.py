# test_database.py
from app import create_app
from models import db, User, FavoriteRoute
from datetime import datetime


def test_database_operations():
    app = create_app()

    with app.app_context():
        # 测试数据库连接
        try:
            # 查询用户数量
            user_count = User.query.count()
            print(f"数据库中有 {user_count} 个用户")

            # 创建测试用户
            test_user = User(
                firebase_uid=f"test_uid_{datetime.now().timestamp()}",
                username=f"test_user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                email=f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
            )
            db.session.add(test_user)
            db.session.commit()
            print(f"创建测试用户成功，ID: {test_user.id}")

            # 添加收藏路线
            favorite = FavoriteRoute(
                user_id=test_user.id,
                route_id="TEST"
            )
            db.session.add(favorite)
            db.session.commit()
            print(f"添加收藏路线成功")

            # 查询收藏
            favorites = FavoriteRoute.query.filter_by(user_id=test_user.id).all()
            print(f"用户收藏数量: {len(favorites)}")

            print("\n数据库测试成功！")

        except Exception as e:
            print(f"数据库测试失败: {e}")


if __name__ == "__main__":
    test_database_operations()