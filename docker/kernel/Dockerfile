###################################################################################################
# Base
# Create a common image with pip requirements installed
FROM perceptilabs.azurecr.io/cuda11.0.3-cudnn8-devel-py36-ubi8 as base

USER 0

WORKDIR /src
ADD requirements.txt ./
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt
RUN rm requirements.txt

# ###################################################################################################
# build
FROM base as build

RUN yum -y update && \
    yum -y install rsync \
           python3-devel && \
    ln -sf $(which python3) $(dirname $(which python3))/python
    # Installing python3-devel can undo the link from the base image. Make sure it stays.

# add source
# do the build in here
WORKDIR /src
ADD included_files.txt requirements_build.txt ./
ADD perceptilabs ./perceptilabs

RUN pip install -r requirements_build.txt

# Train the ram estimator
WORKDIR /src/perceptilabs/insights/csv_ram_estimator
RUN python train_model.py data_1579288530.csv

WORKDIR /out
# Set up the out dir for the build
ADD main.py setup.py setup.cfg package_data.json VERSION cython_roots.txt requirements.txt ./
RUN rsync -a /src --files-from=/src/included_files.txt .
RUN mv perceptilabs/tutorial_data /tutorial_data
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

LABEL name="PerceptiLabs-Modelling-Backend" \
      maintainer="contact@perceptilabs.com" \
      vendor="PerceptiLabs" \
      version="replaceme" \
      release="1" \
      summary="This is the free version of the backend of our modelling platform v1." \
      description="This will build a server for you which will act as a backend for our modelling platform. It listens to port 5000 to communicate with the frontend."

USER 0

WORKDIR /opt/app-root/src
COPY --from=build --chown=1001 /out .
COPY --from=build --chown=1001 /tutorial_data /tutorial_data

# https://github.com/tensorflow/tensorflow/issues/44777
# Fake it out until TF supports libcusolver.so.11
RUN ln -Ffs /usr/local/cuda/targets/x86_64-linux/lib/libcusolver.so.11 /usr/local/cuda/targets/x86_64-linux/lib/libcusolver.so.10

USER 1001

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/lib64:/usr/local/cuda/compat:/usr/local/cuda/targets/x86_64-linux/lib

COPY licenses /licenses

# feature flags
ENV PL_IOU=1
ENV PL_KERNEL_TRAINER=standard

# TODO: add healthcheck for websocket and REST apis

CMD ["python3.6", "-u", "main.py", "-p=browser"]
