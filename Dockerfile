FROM python:3.14-slim@sha256:a7fb1e634c4a578f9e0bd6327f11a3cde11b7a9395f48e24360c0988bcc5c2bc

WORKDIR /opt/council
COPY . .

RUN python3 tools/council_dist.py verify \
    && python3 -m unittest discover -s tests -v \
    && python3 tools/council_dist.py release --output /tmp/council-release

ENTRYPOINT ["python3", "tools/council_dist.py"]
CMD ["verify"]
