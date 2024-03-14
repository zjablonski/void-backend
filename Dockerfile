# Use the official Python image with your required version
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy the pyproject.toml and poetry.lock files (if available) to the container
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry:
# - Do not create a virtual environment inside the container, as it's unnecessary
# - Install only package dependencies (skip dev-dependencies)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of your application code to the container
COPY . /app
