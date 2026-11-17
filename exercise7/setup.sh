#!/bin/sh
# Generates both Synapse homeservers (own + simulated partner), applies the
# exercise settings and creates the self-signed federation certificate.
# Usage: ./setup.sh   (then: docker compose up -d)
set -e
cd "$(dirname "$0")"
A=cr261517.matrix.test
B=partner.matrix.test

mkdir -p hsA hsB
for pair in "A:$A" "B:$B"; do
  n=${pair%%:*}; d=${pair#*:}
  docker run --rm -v "$PWD/hs$n:/data" -e SYNAPSE_SERVER_NAME=$d -e SYNAPSE_REPORT_STATS=no \
    matrixdotorg/synapse:latest generate
  python3 - "hs$n/homeserver.yaml" <<'EOF'
import sys
f = sys.argv[1]
s = open(f).read()
s = s.replace('trusted_key_servers:\n  - server_name: "matrix.org"\n', 'trusted_key_servers: []\n')
s = s.replace("# vim:ft=yaml", open("exercise_settings.yaml").read() + "\n# vim:ft=yaml")
open(f, "w").write(s)
EOF
done

openssl req -x509 -newkey rsa:2048 -nodes -days 365 -keyout nginx/key.pem -out nginx/cert.pem \
  -subj "/CN=matrix.test" -addext "subjectAltName=DNS:$A,DNS:$B"
