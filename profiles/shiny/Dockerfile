FROM rocker/shiny:4.4.1

RUN current_uid="$(id -u shiny)" \
    && if [ "$current_uid" != "999" ]; then usermod -u 999 shiny; fi \
    && mkdir -p /home/shiny /srv/shiny-server \
    && chown -R 999:999 /home/shiny /srv/shiny-server

RUN rm -rf /srv/shiny-server/*
COPY --chown=shiny:shiny app/ /srv/shiny-server/

USER shiny
WORKDIR /srv/shiny-server
EXPOSE 3838
CMD ["/usr/bin/shiny-server"]
