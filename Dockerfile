# Use an official Python runtime as a base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the content of the local src directory to the working directory
COPY ./src /app/src

# Copy the requirements.txt file to the working directory
#COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt

# Install TensorFlow and PyTorch
RUN pip install tensorflow torch beautifulsoup4 requests tqdm transformers

# Run the main.py script when the container launches
CMD ["python", "/app/src/main.py"]
