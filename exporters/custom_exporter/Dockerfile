FROM python:3.10-slim
WORKDIR /app
COPY custom_exporter.py .
RUN pip install prometheus_client requests
CMD ["python", "custom_exporter.py"]
EXPOSE 8000
