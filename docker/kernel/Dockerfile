###################################################################################################
# Base
# Create a common image with pip requirements installed
FROM quay.io/perceptilabs/cuda11.2.2-cudnn8-devel-py38-ubi8 as base

USER 0

WORKDIR /src
ADD requirements.txt ./
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt
RUN rm requirements.txt

# ###################################################################################################
# build
FROM base as build

# Don't refresh the nvidia packages since we're not using them (https://forums.developer.nvidia.com/t/error-apt-get-updating-from-nvidia-cuda11-2-1-base-ubuntu20-04/209836/10)
RUN rm /etc/yum.repos.d/nvidia-ml.repo /etc/yum.repos.d/cuda.repo && \
    yum -y update && \
    yum -y install rsync && \
    yum clean all

# add source
# do the build in here
WORKDIR /src
ADD included_files.txt requirements_build.txt ./
ADD perceptilabs ./perceptilabs

RUN pip install -r requirements_build.txt

WORKDIR /out
# Set up the out dir for the build
ADD main.py setup.py setup.cfg package_data.json VERSION cython_roots.txt requirements.txt ./
RUN rsync -a /src --files-from=/src/included_files.txt .
RUN rm -rf /src
RUN mv main.py main.pyx
RUN find . -name "__init__.py" -exec mv '{}' '{}x' \;
RUN python setup.py build_ext --inplace --user
RUN find . -type f -name '*.c' -exec rm '{}' \;
RUN find . -type f -name '*.py' -exec rm '{}' \;
RUN rm -r build
RUN mv main.pyx main.py
RUN find . -name "__init__.pyx" | xargs dirname | xargs -I {} mv '{}/__init__.pyx' '{}/__init__.py'

# ###################################################################################################
# publish
FROM base

LABEL name="PerceptiLabs-Modeling-Backend" \
      maintainer="contact@perceptilabs.com" \
      vendor="PerceptiLabs" \
      version="replaceme" \
      release="1" \
      summary="This is the free version of the backend of our modeling platform v1." \
      description="This will build a server for you which will act as a backend for our modeling platform."

USER 0

WORKDIR /opt/app-root/src
COPY --from=build --chown=1001 /out .
ADD run_worker_from_config.py queues.yaml ./
RUN mkdir /tutorial_data
RUN chown 1001 /tutorial_data

USER 1001

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/lib64:/usr/local/cuda/compat:/usr/local/cuda/targets/x86_64-linux/lib

COPY licenses /licenses

# feature flags
ENV PL_IOU=1
ENV PL_KERNEL_TRAINER=standard

# TODO: add healthcheck for websocket and REST apis

CMD ["python3.8", "-u", "main.py"]
