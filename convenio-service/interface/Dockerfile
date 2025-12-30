FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY convenio_interface.py .

EXPOSE 5000

CMD ["python", "convenio_interface.py"]