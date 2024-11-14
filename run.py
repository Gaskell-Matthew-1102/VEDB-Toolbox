# run.py

from app import create_app  # Import the create_app function from app/__init__.py

def run():
    # Create the Flask app using the factory function
    app = create_app()

    # Run the app
    app.run()

if __name__ == "__main__":
    run()
