FROM registry.access.redhat.com/ubi8/python-36
#FROM tensorflow/tensorflow:1.15.0-gpu-py3

LABEL name="PerceptiLabs-Modelling-Backend" \
      vendor="PerceptiLabs" \
      version="1.0" \
      release="1" \
      summary="This is the free version of the backend of our modelling platform v1." \
      description="This will build a server for you which will act as a backend for our modelling platform. It listens to port 5000 to communicate with the frontend." 


COPY licenses /licenses


USER 0
RUN yum -y --nodocs update && \
    yum -y --nodocs install ncurses-devel && \
    yum clean all
USER 1001

#USER 0
#RUN apt-get update && \
#    apt-get install -y ncurses-devel
#USER 1001 

ADD . /opt/app-root/src

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install --upgrade setuptools

WORKDIR /opt/app-root/src

EXPOSE 5000

CMD ["python3.6", "-u", "webServer.py"]

#######################################################################
# FROM registry.access.redhat.com/ubi7-dev-preview/ubi

# RUN yum update

# RUN yum -y install gcc gcc-c++ make kernel-devel zlib-devel bzip2 bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel expat-devel wget

# RUN wget http://python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz
# RUN tar xf Python-3.6.3.tar.xz
# WORKDIR /Python-3.6.3

# RUN ./configure --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
# RUN make && make altinstall

# RUN wget https://bootstrap.pypa.io/get-pip.py
# RUN python3.6 get-pip.py

# ADD . /app

# RUN pip install -r /app/requirements.txt
# RUN pip install --upgrade setuptools

# WORKDIR /app

# # RUN  /usr/local/bin/python3.6 setup.pyx develop

# # RUN rm *.py *.c

# # RUN mv webServer.pyx webServer.py

# EXPOSE 5000

# CMD ["/usr/local/bin/python3.6", "-u", "webServer.py"]
######################################################################
# FROM tensorflow/tensorflow:latest-py3
# # FROM python:3.6.8
# ADD . /app
# WORKDIR /app
# EXPOSE 5000
# RUN pip install -r requirements.txt
# CMD ["python", "-u", "webServer.py"]