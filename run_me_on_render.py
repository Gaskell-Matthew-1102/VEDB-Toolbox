# run_me_on_render.py

from flaskr import create_app  # Import the create_app function from app/__init__.py

def run():
    # Create the Flask app using the factory function
    app = create_app(test_config=None)

    # Run the app
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    run()
