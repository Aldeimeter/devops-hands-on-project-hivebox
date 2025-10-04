FROM ubuntu:22.04

WORKDIR /opt/hivebox

COPY ./version.sh .

CMD ["./version.sh"]
