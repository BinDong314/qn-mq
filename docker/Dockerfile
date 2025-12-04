FROM python:3.10-slim

ARG QN_MQ_REF="develop"

RUN echo "--- Use the Dockerfile under rood --" 

# Install packages
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    git \
    && apt-get clean

# Update pip
RUN pip install --upgrade pip setuptools wheel

RUN --mount=type=secret,id=GH_TOKEN \
    export GH_TOKEN=$(cat /run/secrets/GH_TOKEN) && \
    git clone https://${GH_TOKEN}@github.com/quant-net/quant-net-mq -b ${QN_MQ_REF}


RUN cd quant-net-mq && pip install . && cd ../

CMD ["quantnet_mq"]
