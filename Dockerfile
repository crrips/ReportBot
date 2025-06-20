FROM python:3.11

WORKDIR /.

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3.11", "src/main.py"]