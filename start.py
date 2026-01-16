from app import create_app, db
from flask_migrate import upgrade
import logging

# Configure logging to show INFO messages
logging.basicConfig(level=logging.INFO)

#Start
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        upgrade()  # Run database migrations
    app.run()