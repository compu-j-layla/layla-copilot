FROM ubuntu:latest
RUN apt-get update
RUN apt-get install -y --reinstall python3-dev python3-pip python3.14-venv python3-full
COPY requirements.txt ./
RUN python3 -m venv myvenv/
RUN myvenv/bin/pip3 install --no-cache-dir --upgrade pip \
  && myvenv/bin/pip3 install --no-cache-dir -r requirements.txt
COPY run.sh run.sh
RUN ["chmod", "+x", "run.sh"]
CMD ./run.sh