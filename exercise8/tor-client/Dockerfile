FROM alpine:3.20
RUN apk add --no-cache tor curl
COPY torrc /etc/tor/torrc
USER tor
CMD ["tor", "-f", "/etc/tor/torrc"]
