################
# BUILD PHASE
################
FROM registry.access.redhat.com/ubi8/nodejs-12 as build_npm

USER 0
WORKDIR /app
ADD package-lock.json package.json ./
ADD src/ ./src/
ADD static/ ./static/

RUN npm install --unsafe-perm=true --allow-root && \
    npm run build-docker


################
# PUBLISH PHASE
################
FROM registry.access.redhat.com/ubi8/python-36

LABEL name="PerceptiLabs-Modeling-Web-app" \
      vendor="PerceptiLabs" \
      version="Development" \
      release="1" \
      summary="This is the free version of the frontend of our modeling platform v1." \
      description="This will build a web app for you which will act as a frontend for our modeling platform. It listens to port 8080:80 to communicate with the backend." 

USER 0
WORKDIR /app

ADD static_file_server/static_file_server /app/static_file_server/
ADD static_file_server/manage.py static_file_server/requirements.txt /app/
ADD licenses /licenses

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm requirements.txt

COPY --from=build_npm /app/src/dist/ /app/static_file_server/dist/

EXPOSE 8080

CMD ["python", "-m", "django", "runserver", "0.0.0.0:8080", "--settings", "static_file_server.settings", "--noreload"]
