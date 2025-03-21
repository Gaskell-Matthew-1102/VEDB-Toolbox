FROM python:slim-bookworm

WORKDIR /app

RUN apt update && apt install -y libgl1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 10000
CMD ["gunicorn", "-b", "0.0.0.0:10000", "-w", "2", "flaskr:create_app(test_config=None)"]