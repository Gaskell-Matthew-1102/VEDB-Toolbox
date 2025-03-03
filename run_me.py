# run.py

from flaskr import create_app  # Import the create_app function from app/__init__.py

def run():
    # Create the Flask app using the factory function
    app = create_app(test_config=None)

    # Run the app
    app.run()

if __name__ == "__main__":
    run()
