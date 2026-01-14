from app import create_app, db

app = create_app()

with app.app_context():
    from sqlalchemy import text
    db.session.execute(text("DROP TABLE IF EXISTS lesson;"))
    db.session.execute(text("DROP TABLE IF EXISTS day;"))
    db.session.commit()
    print("Dropped day and lesson tables")