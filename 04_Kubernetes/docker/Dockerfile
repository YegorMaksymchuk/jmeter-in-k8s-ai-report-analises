FROM justb4/jmeter:5.5

WORKDIR $JMETER_HOME 

COPY plugins/ lib/ext/
COPY config/user.properties bin/user.properties
COPY scripts/install_plugin-manager.sh .
COPY scripts/docker-entrypoint.sh /docker-entrypoint.sh
COPY test/  test/


RUN chmod +x install_plugin-manager.sh /docker-entrypoint.sh
RUN ./install_plugin-manager.sh

EXPOSE 6000 1099 50000
ENTRYPOINT ["/docker-entrypoint.sh"]