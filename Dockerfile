FROM python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36

WORKDIR /opt/council
COPY . .

RUN python3 tools/council_dist.py verify \
    && python3 -m unittest discover -s tests -v \
    && python3 tools/council_dist.py release --output /tmp/council-release

ENTRYPOINT ["python3", "tools/council_dist.py"]
CMD ["verify"]
