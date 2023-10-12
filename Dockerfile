# Use an official Python 3.10 runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app/
COPY ./requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the Flask application code from flask_app_backup/ into the container at /app/
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 80

# Set environment variables
ENV SECRET_KEY=${SECRET_KEY}
ENV DATABASE_URL=${DATABASE_URL}
ENV FLASK_APP=${FLASK_APP}

# Run app.py when the container launches
CMD [ "flask", "run", "--host=0.0.0.0", "--port=5000" ]