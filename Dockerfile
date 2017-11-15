FROM elyase/conda:2.7

LABEL maintainer="costa.marcos.pro@gmail.com"

COPY . /tjbot
WORKDIR /tjbot

RUN conda install pip && pip install -r requirements.txt
