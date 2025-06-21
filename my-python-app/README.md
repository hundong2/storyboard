# My Python App

This project is a simple Python application that runs inside a Docker container. Below are the instructions on how to build and run the application.

## Project Structure

```
my-python-app
├── Dockerfile
├── requirements.txt
├── test.py
└── README.md
```

## Requirements

Make sure you have Docker installed on your machine.

## Building the Docker Image

To build the Docker image for this application, navigate to the project directory and run the following command:

```
docker build -t my-python-app .
```

## Running the Docker Container

After building the image, you can run the Docker container using the following command:

```
docker run my-python-app
```

This will execute the `test.py` script inside the container.

## Dependencies

The required Python packages are listed in the `requirements.txt` file. The Dockerfile will automatically install these dependencies when building the image.