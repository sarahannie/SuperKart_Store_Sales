FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files and the serialized model
COPY app.py .
COPY superkart_model.joblib .

# Expose port 7860
EXPOSE 7860

# Run the web application using Gunicorn for production scalability
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
