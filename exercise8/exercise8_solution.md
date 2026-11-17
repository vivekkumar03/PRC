# Exercise 8 – Tor onion service

**Task:** Create an onion service with Tor and access it (Hello World page); create a hidden service for the Matrix server; document it; which browser and why; show circuits for clearnet vs. hidden service and explain the difference; find news sites/public services with onion services.

## Setup (Docker, all files in this folder)

| Container | Role |
|---|---|
| `onion-web` | nginx serving `web/index.html` ("Hello World") |
| `tor-hs` | Tor daemon that publishes **two onion services** (v3) |
| `tor-client` | Separate Tor daemon acting as client: SOCKS proxy `127.0.0.1:9050` (published on the host loopback only) and control port for circuit inspection |

The Matrix homeserver `hsA` of exercise 7 is reached via the Docker network `exercise7_matrixnet`.

### Configuration (`tor-hs/torrc`)
```
DataDirectory /var/lib/tor/data
HiddenServiceDir /var/lib/tor/hs_hello
HiddenServiceVersion 3
HiddenServicePort 80 web:80

HiddenServiceDir /var/lib/tor/hs_matrix
HiddenServiceVersion 3
HiddenServicePort 80 hsA:8008
```
Client (`tor-client/torrc`): `SocksPort 0.0.0.0:9050`, `SocksPolicy accept *` (only published on the host's 127.0.0.1), `ControlPort 127.0.0.1:9051`, `CookieAuthentication 1`.

### Steps
```bash
cd exercise7 && docker compose up -d          # Matrix stack (network needed by tor-hs)
cd ../exercise8 && docker compose up -d --build
docker exec tor-hs cat /var/lib/tor/hs_hello/hostname /var/lib/tor/hs_matrix/hostname
```
Tor generates an ed25519 key pair per service; the `.onion` address *is* the public key (base32 + checksum + version), so no registration or DNS is needed:
- Hello World: `xb2eg2ilfsfpcyp6udyxoub4efuqka2pscr7u7rgypbycv4atimb27ad.onion`
- Matrix (client API): `ngxmra3rem5sy5x74kmwpcl25a3sjiyjqkotpzj5q3jaazntjsnatwyd.onion`

(Lab addresses; the private keys are in the Docker volume `hs_keys` and not part of the submission.)

## Result: accessing the services

Through the SOCKS proxy of the separate client (`--socks5-hostname` makes Tor resolve the name; a normal DNS lookup cannot resolve `.onion`):

```
$ curl --socks5-hostname 127.0.0.1:9050 http://xb2eg2ilfsfpcyp6udyxoub4efuqka2pscr7u7rgypbycv4atimb27ad.onion/
<h1>Hello World from a Tor onion service!</h1> ...

$ curl --socks5-hostname 127.0.0.1:9050 http://ngxmra3rem5sy5x74kmwpcl25a3sjiyjqkotpzj5q3jaazntjsnatwyd.onion/_matrix/client/versions
{"versions":["r0.0.1","r0.1.0","r0.2.0", ... "v1.1", ...
```
Both responded during the recorded test through Tor. Availability can change when the service or network is offline. The onion endpoints do not require a public DNS name or inbound port on this host. (For Matrix, a client such as Element must be pointed at this base URL; ordinary federation needs separate setup. Onion-to-onion federation was not tested.)

**Availability check, 14 November 2026:** both onion URLs timed out after 25 seconds through the local Tor proxy; a Firefox-through-Tor attempt also timed out. The Tor logs showed repeated clock jumps, but the cause of the failures was not established.

The uploaded screenshot below separately shows the Hello World onion page
open in Tor Browser. Availability can vary between attempts.

![Hello World onion page in Tor Browser](../img/Tor%20onion%20service.png)

### Pitfalls
- The first bootstrap took several minutes in the container (directory info download: "Bootstrapped 45%" for a long time). Requests to a fresh onion service fail until the service descriptor has been uploaded to the HSDirs, so the first `curl` returned nothing; a retry after a few minutes worked.
- The hidden service container must be on the same Docker network as the target (`hsA`), hence the external network `exercise7_matrixnet`.

## Which browser?
**Tor Browser** is recommended: it routes browser traffic through Tor and includes defenses intended to reduce fingerprinting and cross-site tracking. These protections are not perfect and do not make all users indistinguishable. The original command-line test used `curl` with `--socks5-hostname`; the uploaded screenshots show Tor Browser visiting the Hello World and BBC onion sites.

Other browsers can be used if they are configured to use a Tor SOCKS proxy and to send DNS through it:
- **Firefox** (normal): proxy settings → SOCKS v5 `127.0.0.1:9050`, enable "Proxy DNS when using SOCKS v5" (`network.proxy.socks_remote_dns=true`), and set `network.dns.blockDotOnion=false`.
- **Brave**: "Private window with Tor" (built-in Tor).
- **Chrome/Chromium**: `--proxy-server="socks5://127.0.0.1:9050"`.
But a normal browser is easily fingerprinted/identified (extensions, fonts, WebRTC/DNS leaks, cookies), which undermines the anonymity gained by Tor, so only Tor Browser is advisable for real anonymity.

## Circuits: clearnet vs. hidden service

The following uploaded screenshots show two different circuits to the BBC
onion site. Both are onion-service circuits, **not** a clearnet-versus-onion
comparison; the circuit display indicates the onion site's relay side.

![BBC onion site and first Tor circuit](../img/BBC_Onion%20Site.png)

![BBC onion site and another Tor circuit](../img/BBC_Onion%20Site_DiffCircuit.png)

Script `circuits.sh` (output saved in `circuits_output.txt`) reads `GETINFO circuit-status` from the control port after each request. The general circuits below are visible at that time, but the output does not establish which one carried the clearnet request.

**Clearnet** (`https://check.torproject.org/api/ip` → `{"IsTor":true,"IP":"109.70.100.1"}`), observed general circuits:
```
45 BUILT olivia, kingray, NTH43R2          PURPOSE=GENERAL
46 BUILT as215248tor2a, TheLoneGunmen, lunar9   PURPOSE=GENERAL
```
**Hidden service** (Hello World), purpose `HS_CLIENT_REND` (rendezvous circuit, flag `IS_INTERNAL`, `HS_STATE=HSCR_JOINED`) and `HS_CLIENT_HSDIR` (descriptor lookup):
```
43 BUILT as215248tor2a, evers, NTH161R1                    PURPOSE=HS_CLIENT_REND  HS_STATE=HSCR_JOINED REND_QUERY=xb2eg2il...
33 BUILT as215248tor2a, evers, FloTheDev, p1onX01           PURPOSE=HS_CLIENT_HSDIR
```
Why they differ:
- **Clearnet:** a connection to an ordinary internet site uses an *exit relay*. The exit sees the destination and can see plaintext without HTTPS; the destination sees the exit IP. Tor is designed so that no single relay knows both the client and destination, but traffic analysis remains a risk.
- **Onion service:** no clearnet exit is used. The client obtains a descriptor from HSDirs and contacts an introduction point; client and service then connect through a rendezvous point using separate circuits. The exact circuit lengths vary; the shown rendezvous circuit is the client side. Onion connections provide encryption and authentication for the onion address, but do not guarantee anonymity or immunity from attacks.
- Costs: higher latency (more hops, descriptor lookup, rendezvous setup); this is why the first request was slow.

## Onion services of news sites and public services

Results recorded through the Tor client at the time (`onion_sites.txt`); these addresses and availability may have changed:

| Service | Onion address | Result |
|---|---|---|
| BBC News | `bbcnewsd73hkzno2ini43t4gblxvycyac5aw4gnv7t2rccijh7745uqd.onion` | 301 (redirect, reachable) |
| DuckDuckGo | `duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion` | 200 |
| Proton Mail | `protonmailrmez3lotccipshtkleegetolb73fuirgj7r4o4vfu7ozyd.onion` | 200 |
| New York Times | `nytimesn7cgmftshazwhfgzm37qxb44r64ytbb2dj3x62d2lljsciiyd.onion` | timeout in my test; current availability unverified |
| Tor Project | `2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion` | timeout in my test |

Reasons for onion services include reaching users in censoring countries, protecting readers' privacy, avoiding exit-node interception and enabling source contact. Check addresses against each provider's official site before using them.

## Remaining verification
The uploaded screenshots show Tor Browser accessing the Hello World and BBC onion pages and displaying BBC onion circuits. A clearnet circuit screenshot and a request-specific clearnet-versus-onion comparison remain outstanding; the Matrix onion API was not shown in these screenshots.

## Cleanup
`docker compose down` stops the services. Retain the onion-key volume to keep the same addresses.
