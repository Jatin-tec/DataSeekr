# Use the official NVIDIA CUDA and CuDNN base image with PyTorch
FROM pytorch/pytorch:1.10.0-cuda12.0-cudnn8-runtime

# Install Nvidia Docker runtime (nvidia-docker2)
RUN distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
    && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add - \
    && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list

RUN apt-get update && apt-get install -y nvidia-docker2

# Set working directory
WORKDIR /app

# Copy your code into the container
COPY . /app/.

RUN chmod +x requirements.sh
RUN ./requirements.sh

# Command to run your code
CMD ["python", "model.py"]