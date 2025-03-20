FROM debian:stable-slim
WORKDIR /app
RUN apt update && apt install -y libgl1-mesa-glx python3-{full,pip}
COPY ./requirements.txt requirements.txt
RUN python3 -m venv toolboxenv && source toolboxenv/bin/activate
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
EXPOSE 10000
CMD ["gunicorn", "-b", "0.0.0.0:10000", "-w", "2", "flaskr:create_app(test_config=None)"]