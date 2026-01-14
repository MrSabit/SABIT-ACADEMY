from app import create_app, db

app = create_app()

with app.app_context():
    from sqlalchemy import text
    result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = [row[0] for row in result]
    print("Tables:", tables)