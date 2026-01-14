from app import create_app, db
from app.models import User, Day, Lesson, Note, Assignment, Submission

app = create_app()
with app.app_context():
    # Keep only the main admin (assume id=1)
    admin = User.query.get(1)
    if admin:
        User.query.filter(User.id != 1).delete()
    else:
        print("No admin with id=1 found. No users kept.")
    # Delete all other data
    Day.query.delete()
    Lesson.query.delete()
    Note.query.delete()
    Assignment.query.delete()
    Submission.query.delete()
    db.session.commit()
    print("Database cleared except for main admin.")
