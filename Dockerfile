FROM elyase/conda:2.7

ARG api_key
ENV TJBOT_API_KEY=$api_key

ADD . /tjbot
WORKDIR /tjbot

RUN conda install pip && pip install -r requirements.txt
