FROM osgeo/gdal:ubuntu-small-latest

RUN apt-get update
RUN apt-get -y install python3-pip

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Authorize SSH Host
RUN mkdir -p /root/.ssh
COPY ./resources/keys/id_rsa /root/.ssh
RUN chmod 0700 /root/.ssh && \
    ssh-keyscan github.com > /root/.ssh/known_hosts && \
    chmod 600 /root/.ssh/id_rsa

RUN pip3 install git+ssh://git@github.com/ECHOESProj/eo-io.git

COPY eo_custom_scripts /app/eo_custom_scripts
WORKDIR /app/

ENTRYPOINT  [ "python3", "-W", "ignore", "-m", "eo_custom_scripts" ]