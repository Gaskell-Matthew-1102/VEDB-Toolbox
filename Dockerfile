FROM python:slim
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
CMD ["gunicorn", "-b", "0.0.0.0", "-w", "2", "flaskr:create_app(test_config=None)"]