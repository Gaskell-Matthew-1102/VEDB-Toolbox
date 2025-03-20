FROM debian:stable-slim
WORKDIR /app
RUN apt update && apt install -y libgl1-mesa-glx
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
EXPOSE 10000
CMD ["gunicorn", "-b", "0.0.0.0:10000", "-w", "2", "flaskr:create_app(test_config=None)"]