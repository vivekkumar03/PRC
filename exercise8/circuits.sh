#!/bin/sh
# Usage: ./circuits.sh   (run from exercise8/, containers must be up)
# Shows the Tor circuits used for a clearnet site vs. our hidden service.
H=$(docker exec tor-hs cat /var/lib/tor/hs_hello/hostname)
SOCKS="--socks5-hostname 127.0.0.1:9050"

show() {
  docker exec tor-client sh -c '
    C=$(od -An -v -tx1 /var/lib/tor/data/control_auth_cookie | tr -d " \n")
    printf "AUTHENTICATE %s\r\nGETINFO circuit-status\r\nQUIT\r\n" "$C" | nc 127.0.0.1 9051' \
  | grep -E "^[0-9]+ (BUILT|EXTENDED)" | grep -E "$1"
}

echo "== 1) clearnet: https://check.torproject.org/api/ip"
docker exec tor-client curl -s -m 60 $SOCKS https://check.torproject.org/api/ip; echo
echo "-- circuit (GENERAL, 3 hops: guard, middle, exit):"
show "PURPOSE=GENERAL" | tail -2

echo; echo "== 2) hidden service: http://$H/"
docker exec tor-client curl -s -m 120 $SOCKS http://$H/ | grep -o "<h1>.*</h1>"
echo "-- circuits (HS_CLIENT_*: towards introduction point and rendezvous point):"
show "PURPOSE=HS_CLIENT" | tail -4
