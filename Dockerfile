FROM python:3.9

RUN apt-get update
RUN apt-get -qq -y install gcc libgflags2.2 libgflags-dev libgflags-dev zlib1g-dev libzstd-dev python3-setuptools python3-wheel python3-pip
RUN pip3 install --upgrade pip
RUN pip3 uninstall numpy
RUN pip3 uninstall spacy
RUN pip3 install numpy
RUN pip3 install regex 'spacy~=3.2.4' pytest cython
RUN python3 -m spacy download en && python3 -m spacy download en_core_web_sm

VOLUME ["/input", "/output_aliasmap", "/output_recognition", "/databases", "/mappings", "/evaluation", "/log", "/test_input", "/test_output", "/test_databases", "/env"]

WORKDIR /app

COPY . .

RUN python3 setup.py build_ext --inplace

ADD Makefile /app

ENTRYPOINT ["/bin/bash"]

echo "Welcome to WiNERli 2.0!"
echo "WiNERli 2.0 is an improved and extended version of WiNERli, a system that can create an aliasmap from a Wikipedia dump and perform entity recognition on a Wikipedia dump after an aliasmap has been created."
echo "Please run \"make help\" for further information about the available targets that you can use to run WiNERli 2.0 and for further help and details on each target."
echo "If you need further and more detailed information please have a look at the README.md file."
echo "If you want to learn more about the details of what WiNERli 2.0 is doing and how it works you can read the corresponding blog post: https://ad-blog.informatik.uni-freiburg.de/post/introducing-winerli-2.0-an-extension-of-winerli/"

# make docker build
# make docker-run INPUT_ALIASMAP=`pwd`/input OUTPUT_ALIASMAP=`pwd`/databases INPUT_RECOGNITION=`pwd`/input OUTPUT_RECOGNITION=`pwd`/output DATABASES=`pwd`/databases MAPPINGS=`pwd`/mappings EVALUATION=`pwd`/evaluation```
