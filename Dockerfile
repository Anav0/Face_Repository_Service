# This is a sample Dockerfile you can modify to deploy your own app based on face_recognition

FROM python:3.6-slim-stretch
COPY . /DetectingFaces
WORKDIR /DetectingFaces
RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
   # pip3 install -r requirements.txt\
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

ENTRYPOINT ["python"]
CMD ["DetectingFaces.py"]
