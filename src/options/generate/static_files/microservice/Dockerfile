FROM jinaai/jina:3.14.1-py39-standard

RUN apt-get update && apt-get install --no-install-recommends -y {{apt_get_packages}} && apt-get clean && rm -rf /var/lib/apt/lists/*

## install requirements for the executor
COPY requirements.txt .
RUN pip install --compile -r requirements.txt

# setup the workspace
COPY . /workdir/
WORKDIR /workdir

RUN pytest test_microservice.py

ENTRYPOINT ["jina", "executor", "--uses", "config.yml"]