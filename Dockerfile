FROM osgeo/gdal:ubuntu-small-latest

ENV TZ=Europe/Dublin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get update && \
    apt-get install -y python3-pip python3-gdal binutils netcdf-bin libproj-dev gdal-bin libnetcdf-dev \
    libhdf5-serial-dev libproj-dev libgeos-dev proj-data proj-bin docker.io git \

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Authorize SSH Host
RUN mkdir -p /root/.ssh
COPY ./resources/keys/id_rsa /root/.ssh
RUN chmod 0700 /root/.ssh && \
    ssh-keyscan github.com > /root/.ssh/known_hosts && \
    chmod 600 /root/.ssh/id_rsa \

COPY ./resources/eoconfig/creodias.yaml /root/eoconfig/creodias.yaml

RUN pip3 install git+ssh://git@github.com/ECHOESProj/eo-io@main#egg=eo-io && \
    pip3 install git+https://github.com/dcs4cop/xcube.git

COPY eo_custom_scripts /app/eo_custom_scripts
WORKDIR /app/

ENTRYPOINT  [ "python3", "-W", "ignore", "-m", "eo_custom_scripts" ]
