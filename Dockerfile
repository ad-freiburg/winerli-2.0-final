FROM python:3.9

RUN apt-get update
RUN apt-get -qq -y install gcc libgflags2.2 libgflags-dev libgflags-dev zlib1g-dev libzstd-dev python3-setuptools python3-wheel python3-pip
RUN pip3 install --upgrade pip
RUN pip3 uninstall numpy
RUN pip3 uninstall spacy
RUN pip3 install 'numpy==1.26.4'
RUN pip3 install regex 'spacy~=3.2.4' pytest cython
RUN python3 -m spacy download en && python3 -m spacy download en_core_web_sm

VOLUME ["/input", "/output_aliasmap", "/output_recognition", "/databases", "/mappings", "/evaluation", "/log", "/test_input", "/test_output", "/test_databases", "/env"]

WORKDIR /app

COPY . .

RUN python3 setup.py build_ext --inplace

ADD Makefile /app

COPY welcome.sh /etc/profile.d/welcome.sh

ENTRYPOINT ["/bin/bash", "-l", "-c"]

# make docker build
# make docker-run INPUT_ALIASMAP=`pwd`/input OUTPUT_ALIASMAP=`pwd`/databases INPUT_RECOGNITION=`pwd`/input OUTPUT_RECOGNITION=`pwd`/output DATABASES=`pwd`/databases MAPPINGS=`pwd`/mappings EVALUATION=`pwd`/evaluation```
