from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if user already exists
    existing_user = User.query.filter((User.username == 'MiftahulSabit') | (User.email == 'miftahulislamsabit2@gmail.com')).first()
    if existing_user:
        # Update the username, password and role
        existing_user.username = 'MiftahulSabit'
        existing_user.set_password('$abit_098123')
        existing_user.role = 'admin'
        db.session.commit()
        print("Admin user updated successfully.")
    else:
        user = User(username='MiftahulSabit', email='miftahulislamsabit2@gmail.com', role='admin')
        user.set_password('$abit_098123')
        db.session.add(user)
        db.session.commit()
        print("Admin user created successfully.")