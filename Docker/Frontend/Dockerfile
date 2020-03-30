# # FROM centos:centos7
# FROM centos/python-36-centos7

# EXPOSE 8080

# COPY . /var/run/web/

# # CMD cd /var/run/web && python -u simpleServer.py
# #["python", "-u", "simpleServer.py"]
# # CMD cd /var/run/web && python -m SimpleHTTPServer 8080
# CMD cd /var/run/web && python -m http.server 8080

# # FROM trinitronx/python-simplehttpserver

# # EXPOSE 8080

# # COPY . /var/www

###############################################################
FROM registry.access.redhat.com/ubi8
# FROM ubuntu:18.04

LABEL name="PerceptiLabs-Modeling-Web-app" \
      maintainer="dev@perceptilabs.com" \
      vendor="PerceptiLabs" \
      version="1.0" \
      release="1" \
      summary="This is the free version of the frontend of our modeling platform v1." \
      description="This will build a web app for you which will act as a frontend for our modeling platform. It listens to port 8080:80 to communicate with the backend." 


RUN mkdir /licenses
COPY licenses /licenses

RUN yum -y --nodocs update && \
    yum -y --nodocs install httpd && \
    yum clean all && \
    chown -R 0:0 /run/httpd/ /etc/httpd/logs && \
    chmod -R g+wrX /run/httpd/ /etc/httpd/logs 

ADD http.conf /etc/httpd/conf/httpd.conf


ADD . /var/www/html/

EXPOSE 8080

CMD ["/usr/sbin/httpd", "-D", "FOREGROUND"]
# CMD ["./run-httpd.sh"]

#############################################################
# FROM centos:7

# MAINTAINER NewstarCorporation

# RUN yum -y update
# RUN yum -y install httpd

# COPY . /var/www/html/

# ENTRYPOINT ["/usr/sbin/httpd", "-D", "FOREGROUND"]
# # CMD [“/usr/sbin/httpd”, “-D”, “FOREGROUND”]

# EXPOSE 80
