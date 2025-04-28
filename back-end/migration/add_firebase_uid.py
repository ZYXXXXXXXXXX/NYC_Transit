# migrations/add_firebase_uid.py
from app import create_app
from models import db
from sqlalchemy import text


def migrate_database():
    app = create_app()

    with app.app_context():
        try:
            # 添加firebase_uid列
            with db.engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE user ADD COLUMN firebase_uid VARCHAR(128) UNIQUE"
                ))
                conn.commit()
            print("Migration completed: firebase_uid column added")
        except Exception as e:
            print(f"Migration error: {e}")
            # 如果列已存在，会抛出错误，可以忽略


if __name__ == "__main__":
    migrate_database()


# test： python migrations/add_firebase_uid.py