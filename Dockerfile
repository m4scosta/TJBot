FROM elyase/conda:2.7

ADD . /tjbot
WORKDIR /tjbot

RUN conda install pip && pip install -r requirements.txt
