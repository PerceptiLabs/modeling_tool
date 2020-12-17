################
# BUILD PHASE
################
FROM registry.access.redhat.com/ubi7/python-36 as build

USER 0

RUN yum -y update && \
    yum -y install rsync && \
    yum clean all

# add source
# do the build in here
WORKDIR /src
ADD included_files.txt requirements.txt requirements_build.txt ./
ADD perceptilabs ./perceptilabs
ADD fileserver ./fileserver

RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt && \
    pip install -r requirements_build.txt

# Train the ram estimator
WORKDIR /src/perceptilabs/insights/csv_ram_estimator
RUN python train_model.py data_1579288530.csv

WORKDIR /out
# Set up the out dir for the build
ADD runner main.py setup.py setup.cfg package_data.json VERSION cython_roots.txt requirements.txt ./
RUN rsync -a /src --files-from=/src/included_files.txt . && \
    rm -rf /src && \
    mv main.py main.pyx && \
    find . -name "__init__.py" -exec mv '{}' '{}x' \; && \
    python setup.py build_ext --inplace --user && \
    # Remove intermediate files
    find . -type f -name '*.c' -exec rm '{}' \; && \
    find . -type f -name '*.py' -exec rm '{}' \; && \
    rm -r build && \
    mv main.pyx main.py && \
    find . -name "__init__.pyx" | xargs dirname | xargs -I {} mv '{}/__init__.pyx' '{}/__init__.py'


################
# PUBLISH PHASE
################
FROM perceptilabs.azurecr.io/nv_base:7.6.5.32

LABEL name="PerceptiLabs-Modelling-Backend" \
      maintainer="contact@perceptilabs.com" \
      vendor="PerceptiLabs" \
      version="replaceme" \
      release="1" \
      summary="This is the free version of the backend of our modelling platform v1." \
      description="This will build a server for you which will act as a backend for our modelling platform. It listens to port 5000 to communicate with the frontend."

USER 0
RUN yum -y update && \
    yum -y install ncurses-devel libSM libXrender libXext git && \
    yum clean all

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-10.0/compat

WORKDIR /opt/app-root/src
COPY --from=build --chown=1001 /out .
ADD requirements.txt .

RUN chmod +x runner && \
    python -m pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt
    # pip install --no-cache-dir dask[array] --upgrade && \
    # pip install --no-cache-dir  --upgrade dask

USER 1001
COPY licenses /licenses
COPY tutorial_data /tutorial_data

EXPOSE 5000
EXPOSE 8011

CMD ["/opt/app-root/src/runner"]

