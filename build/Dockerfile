FROM docker.io/cm2network/steamcmd:latest

LABEL org.opencontainers.image.source="https://github.com/herheliuk/rust-dedicated"
LABEL org.opencontainers.image.authors="Andrii Herheliuk <andrii@herheliuk.com>"
LABEL org.opencontainers.image.licenses="MIT"

RUN mkdir -p /home/steam/rustserver/server/ \
             /home/steam/rustserver/HarmonyMods/

WORKDIR /home/steam/rustserver/

RUN curl -fL https://github.com/CarbonCommunity/Carbon/releases/download/production_build/Carbon.Linux.Release.tar.gz \
    | tar -xz

COPY --chown=steam:steam . .

RUN chmod +x *.sh

ENTRYPOINT ["./entrypoint.sh"]
