################
# BUILD PHASE
################
FROM registry.access.redhat.com/ubi7/python-36 as build

USER 0

RUN yum -y update && \
    yum -y install rsync

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
    mv perceptilabs/tutorial_data /tutorial_data && \
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
FROM nvcr.io/nvidia/cuda:10.0-cudnn7-devel-ubi7

LABEL name="PerceptiLabs-Modelling-Backend" \
      maintainer="contact@perceptilabs.com" \
      vendor="PerceptiLabs" \
      version="replaceme" \
      release="1" \
      summary="This is the free version of the backend of our modelling platform v1." \
      description="This will build a server for you which will act as a backend for our modelling platform. It listens to port 5000 to communicate with the frontend."

COPY licenses /licenses

USER 1001
WORKDIR /tutorial_data
COPY --from=build --chown=1001 /tutorial_data .

USER 0
RUN yum -y update && \
    yum -y install ncurses-devel rh-python36 rh-python36-pip rh-python36-python-devel rh-python36-python-libs libSM libXrender libXext git && \
    yum clean all

RUN  cd /opt/rh/rh-python36/root/usr/lib64 && \
     ln -s libpython3.6m.so.rh-python36-1.0 libpython3.6m.so.1.0

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-10.0/compat

COPY entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod +x /usr/bin/entrypoint.sh

WORKDIR /opt/app-root/src
COPY --from=build --chown=1001 /out .
RUN chmod +x runner
ADD requirements.txt .


RUN source scl_source enable rh-python36 && \
    python -m pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt
    # pip install --no-cache-dir dask[array] --upgrade && \
    # pip install --no-cache-dir  --upgrade dask

USER 1001

EXPOSE 5000
EXPOSE 8011

ENTRYPOINT [ "/usr/bin/entrypoint.sh" ]

CMD ["/opt/app-root/src/runner"]

