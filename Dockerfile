FROM ubuntu:20.04

ENV TZ=Europe/Dublin

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get update && \
    apt-get install -y python3-pip python3-gdal binutils netcdf-bin libproj-dev gdal-bin libnetcdf-dev \
    libhdf5-serial-dev libproj-dev libgeos-dev proj-data proj-bin docker.io git gettext-base

# Authorize SSH Host (no longer required)
#RUN mkdir -p /root/.ssh
#COPY credentials/config /root/.ssh/
#COPY credentials/*_rsa /root/.ssh/
#COPY credentials/config_eo_service.yml /root/config_eo_service.yml
#RUN chmod 0700 /root/.ssh && \
#    ssh-keyscan github.com > /root/.ssh/known_hosts && \
#    chmod 600 /root/.ssh/config && \
#    chmod 600 /root/.ssh/*_rsa

RUN pip3 install git+https://github.com/ECHOESProj/eo-io.git && \
    pip3 install git+https://github.com/ECHOESProj/eoian.git && \
    pip3 install git+https://github.com/dcs4cop/xcube.git && \
    pip3 install git+https://github.com/dcs4cop/xcube-sh.git

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY ./eo_processors /app/eo-processors
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
WORKDIR /app/eo-processors

ENTRYPOINT ["/app/entrypoint.sh"]
