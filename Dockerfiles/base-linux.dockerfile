FROM ubuntu:focal
LABEL maintainer="a.helm87@gmail.com"

ARG GIT_VERSION="2.30.1"
ARG DUMB_INIT_VERSION="1.2.5"
ARG DOCKER_COMPOSE_VERSION="1.28.4"
ARG GH_ACTION_RUNNER_VERSION="2.277.1"

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    apt-utils \
  && apt-get install -y --no-install-recommends \
    awscli \
    curl \
    tar \
    unzip \
    apt-transport-https \
    ca-certificates \
    sudo \
    gnupg-agent \
    software-properties-common \
    build-essential \
    zlib1g-dev \
    gettext \
    liblttng-ust0 \
    libcurl4-openssl-dev \
    inetutils-ping \
    jq \
    wget \
    dirmngr \
    openssh-client \
    locales \
  && locale-gen en_US.UTF-8 \
  && dpkg-reconfigure locales \
  && c_rehash \
  && cd /tmp \
  && [[ $(lsb_release -cs) == "xenial" ]] && ( wget --quiet "https://github.com/Yelp/dumb-init/releases/download/v${DUMB_INIT_VERSION}/dumb-init_${DUMB_INIT_VERSION}_$(uname -i | sed 's/x86_64/amd64/g').deb" && dpkg -i dumb-init_*.deb && rm dumb-init_*.deb ) || ( apt-get install -y --no-install-recommends dumb-init ) \
  && curl -sL https://www.kernel.org/pub/software/scm/git/git-${GIT_VERSION}.tar.gz -o git.tgz \
  && tar zxf git.tgz \
  && cd git-${GIT_VERSION} \
  && ./configure --prefix=/usr \
  && make \
  && make install \
  && cd / \
  && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - \
  && [[ $(lsb_release -cs) == "focal" ]] && ( add-apt-repository "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu focal stable" ) || ( add-apt-repository "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" ) \
  && apt-get update \
  && apt-get install -y docker-ce docker-ce-cli containerd.io --no-install-recommends --allow-unauthenticated \
  && curl -sL "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
  && chmod +x /usr/local/bin/docker-compose \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf /tmp/*

# enviroment variable is required to run GitHub action runner as root
ENV RUNNER_ALLOW_RUNASROOT=1

WORKDIR /action-runner
RUN curl -O -L https://github.com/actions/runner/releases/download/v${GH_ACTION_RUNNER_VERSION}/actions-runner-linux-x64-${GH_ACTION_RUNNER_VERSION}.tar.gz \
  && tar xzf ./actions-runner-linux-x64-${GH_ACTION_RUNNER_VERSION}.tar.gz \
  && rm actions-runner-linux-x64-${GH_ACTION_RUNNER_VERSION}.tar.gz
