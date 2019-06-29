FROM python:2.7.15-alpine3.8
USER root
ENV prefix=/open-falcon
ENV workdir=$prefix/dashboard

RUN apk add --no-cache \
    ca-certificates bash git g++ perl make \
    py-mysqldb \
    py-pyldap

RUN mkdir -p $prefix

ENV PYTHONPATH "${PYTHONPATH}:/usr/lib/python2.7/site-packages/"
WORKDIR $workdir

COPY pip_requirements.txt pip_requirements.txt
RUN sed -i '/python-ldap/d' ./pip_requirements.txt && pip install -r pip_requirements.txt

ADD ./ ./

ENTRYPOINT ["/bin/sh", "-c"]
