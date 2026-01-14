from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='MiftahulSabit').first()
    if user:
        print(f"User found: {user.username}, email: {user.email}, role: {user.role}")
        if user.check_password('$abit_098123'):
            print("Password is correct")
        else:
            print("Password is incorrect")
    else:
        print("User not found")