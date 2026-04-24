FROM apache/spark:3.5.0

USER root

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /opt/spark/requirements.txt
RUN pip3 install --user -r /opt/spark/requirements.txt
ENV PATH=/root/.local/bin:$PATH

USER ${SPARK_USER}
