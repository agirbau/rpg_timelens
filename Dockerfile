# Use a CUDA base image with cuDNN support
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04

# Proxy environment variables (if needed)
ENV no_proxy="10.81.0.0/16,172.16.0.0/16,localhost"
ENV http_proxy="http://10.81.247.64:8080"
ENV https_proxy="http://10.81.247.64:8080"

# Add .local/bin to PATH for the user
ENV PATH="/home/user/.local/bin:${PATH}"

# Set environment to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary tools and Python 3.9
RUN apt-get update && apt-get install -y \
    wget \
    git \
    curl \
    ffmpeg \
    software-properties-common \
    python3.9 \
    python3.9-venv \
    python3-pip \
    build-essential \
    python3.9-dev \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.9 as the default Python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1 && \
    update-alternatives --set python /usr/bin/python3.9 && \
    update-alternatives --set pip /usr/bin/pip3

# Upgrade pip
RUN python -m pip install --upgrade pip

# Add a non-root user
RUN useradd -ms /bin/bash user

# Make application and dataset directories
RUN mkdir -p /home/user/app /home/user/dataset /home/user/.local

# Copy the requirements file
COPY eval_scripts/rpg_event_based_frame_interpolation_evaluation/requirements.txt /home/user/app/eval_requirements.txt

# Set permissions for the user
RUN chown -R user:user /home/user

# Switch to non-root user
USER user

# Set working directory
WORKDIR /home/user/app

# Install Python dependencies using pip
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118 && \
    pip install opencv-python scipy tqdm click

RUN pip install -r eval_requirements.txt

# Download the checkpoint and example data
#RUN wget http://download.ifi.uzh.ch/rpg/web/data/timelens/data2/checkpoint.bin && \
#    wget http://download.ifi.uzh.ch/rpg/web/data/timelens/data2/example_github.zip && \
#    unzip example_github.zip && \
#    rm -f example_github.zip

# Set the default command to run
CMD ["/bin/bash"]