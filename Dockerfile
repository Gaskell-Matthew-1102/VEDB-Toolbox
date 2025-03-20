FROM debian:stable-slim
WORKDIR /app

# Install dependencies
RUN apt update && \
    apt install -y libgl1-mesa-glx python3 python3-pip curl pipx && \
    # Ensure pipx uses the correct path for python3
    pipx ensurepath

# Copy and install Python dependencies
COPY ./requirements.txt requirements.txt
RUN pipx inject -r requirements.txt

# Copy the application code
COPY . .

# Expose port
EXPOSE 10000

# Run the app with Gunicorn using pipx
CMD ["pipx", "run", "gunicorn", "-b", "0.0.0.0:10000", "-w", "2", "flaskr:create_app(test_config=None)"]
