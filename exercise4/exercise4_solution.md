# Exercise 4: European eID and trust architecture

The European eIDAS framework does not replace national identity schemes with
one universal identity provider. Member States notify their own schemes and,
subject to the regulation's conditions, recognise eligible notified schemes
from other countries for cross-border access to public services. The schemes
can use different technologies and trust arrangements; it is therefore
incorrect to assume that every national login uses an identical root-to-citizen
certificate hierarchy. In the eIDAS interoperability framework, national
nodes exchange authentication information between the service's country and
the user's country. This federation of national systems resembles a
web-of-trust **only as an analogy**: recognition is based on a legal framework,
notification, assurance requirements and institutional supervision, not
individuals freely signing one another's keys as in PGP. Separately, qualified
trust services such as electronic signatures use national trusted lists,
published by each country and made accessible by the European Commission;
the lists support validation of qualified services and should not be confused
with the authentication-node protocol.

A likely reason for this federated architecture is to achieve interoperability
while respecting national control of identity and building on existing
national systems, legislation and investments. It avoids requiring all
countries to replace their systems with a single technical design, but makes
reliable governance, compatible assurance levels and secure operation by each
participant essential. This explanation is an architectural interpretation,
not a claim that one compromised service can never affect other countries.

## Sources

- [European Commission: eIDAS regulation](https://digital-strategy.ec.europa.eu/en/policies/eidas-regulation)
- [European Commission: EU trusted lists](https://digital-strategy.ec.europa.eu/en/policies/eu-trusted-lists)
- [Regulation (EU) 2024/1183, European Digital Identity Framework](https://eur-lex.europa.eu/eli/reg/2024/1183/oj)
