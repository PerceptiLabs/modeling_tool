################
# BUILD PHASE
################
FROM registry.access.redhat.com/ubi8/nodejs-12 as build

USER 0
WORKDIR /app
ADD . .
RUN rm -rf node_modules && \
    npm install --unsafe-perm=true --allow-root && \
    npm run build-render

################
# PUBLISH PHASE
################
FROM registry.access.redhat.com/ubi8

LABEL name="PerceptiLabs-Modeling-Web-app" \
      vendor="PerceptiLabs" \
      version="Development" \
      release="1" \
      summary="This is the free version of the frontend of our modeling platform v1." \
      description="This will build a web app for you which will act as a frontend for our modeling platform. It listens to port 8080:80 to communicate with the backend." 


COPY licenses /licenses

RUN yum -y --nodocs update && \
    yum -y --nodocs install httpd && \
    yum clean all && \
    chown -R 0:0 /run/httpd/ /etc/httpd/logs && \
    chmod -R g+wrX /run/httpd/ /etc/httpd/logs 

ADD http.conf /etc/httpd/conf/httpd.conf
COPY --from=build /app/src/dist/ /var/www/html/
EXPOSE 8080

CMD ["/usr/sbin/httpd", "-D", "FOREGROUND"]
