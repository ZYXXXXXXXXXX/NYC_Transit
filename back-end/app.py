from flask import Flask
from flask_cors import CORS
from api import create_routes
from models import db
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)

    # 加载配置
    app.config.from_pyfile('config.py')

    # 初始化数据库
    db.init_app(app)

    # 初始化迁移
    migrate = Migrate(app, db)

    # 启用CORS
    CORS(app)

    # 注册路由
    create_routes(app)

    return app


if __name__ == '__main__':
    app = create_app()

    # 创建数据库表（仅开发环境使用）
    with app.app_context():
        db.create_all()

    app.run(debug=True)