FROM redis:6.0.8

RUN apt-get update
RUN apt-get install -y gettext-base
RUN mkdir /var/redis
RUN mkdir /var/redis/7001
RUN mkdir /etc/redis
RUN mkdir /etc/redis/logs

COPY redis_init_script /etc/init.d/redis_7001
COPY redis.conf /etc/redis/7001.conf

RUN chmod 764 /etc/init.d/redis_7001
RUN chmod 777 /var/redis/7001

RUN update-rc.d redis_7001 defaults