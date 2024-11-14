# app/app.py

from app import create_app

# Create the Flask app instance using the factory function
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)  # You can control debug mode here or via config
