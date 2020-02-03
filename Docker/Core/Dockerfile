FROM nvcr.io/nvidia/cuda:10.0-cudnn7-devel-ubi7

LABEL name="PerceptiLabs-Modelling-Backend" \
      maintainer="contact@perceptilabs.com" \
      vendor="PerceptiLabs" \
      version="1.0" \
      release="1" \
      summary="This is the free version of the backend of our modelling platform v1." \
      description="This will build a server for you which will act as a backend for our modelling platform. It listens to port 5000 to communicate with the frontend."

COPY licenses /licenses

USER 0
RUN yum -y update && \
    yum -y install ncurses-devel rh-python36 rh-python36-pip rh-python36-python-devel rh-python36-python-libs && \
    yum clean all

RUN  cd /opt/rh/rh-python36/root/usr/lib64 && \
     ln -s libpython3.6m.so.rh-python36-1.0 libpython3.6m.so.1.0

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-10.0/compat

ADD --chown=1001 . /opt/app-root/src

COPY entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod +x /usr/bin/entrypoint.sh

WORKDIR /opt/app-root/src

RUN source scl_source enable rh-python36 && \
    python -m pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install --no-cache-dir -r requirements.txt
    # pip install --no-cache-dir dask[array] --upgrade && \
    # pip install --no-cache-dir  --upgrade dask
    

USER 1001

EXPOSE 5000

ENTRYPOINT [ "/usr/bin/entrypoint.sh" ]

CMD ["python3.6", "-u", "main.py"]



####################################################################

# FROM nvcr.io/nvidia/cuda:10.1-cudnn7-devel-ubi8

# LABEL name="PerceptiLabs-Modelling-Backend" \
#       vendor="PerceptiLabs" \
#       version="1.0" \
#       release="1" \
#       summary="This is the free version of the backend of our modelling platform v1." \
#       description="This will build a server for you which will act as a backend for our modelling platform. It listens to port 5000 to communicate with the frontend."

# COPY licenses /licenses

# #python3-libs?

# USER 0
# RUN yum -y --nodocs update && \
#     yum -y --nodocs install ncurses-devel python36 python3-pip  python36-devel && \
#     yum clean all

# ADD --chown=1001 . /opt/app-root/src

# WORKDIR /opt/app-root/src

# RUN python3.6 -m pip install --upgrade pip && \
#     pip3 install --upgrade setuptools && \
#     pip3 install --no-cache-dir -r requirements.txt

# USER 1001

# EXPOSE 5000

# CMD ["python3.6", "-u", "webServer.py"]
