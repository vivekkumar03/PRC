# Exercise 3: RSA Encryption

[View Exercise 3 on GitHub](https://github.com/vivekkumar03/PRC/tree/main/exercise3)

## Problem

Use the supplied RSA key pair to encrypt the integer message `99`. Show the calculation steps and intermediate results, explain how to handle the public and private keys, and describe which key is used for encryption, decryption, signing, and verification.

## Given Values

- Message: `m = 99`
- Modulus: `n = 187`
- Public exponent: `e = 7`
- Private exponent: `d = 23`
- Public key: `(e, n) = (7, 187)`
- Private key: `(d, n) = (23, 187)`

The modulus factors as `187 = 11 * 17`, so Euler's totient is:

```text
phi(n) = (11 - 1) * (17 - 1) = 160
```

The exponents form a valid pair because:

```text
e * d = 7 * 23 = 161 = 1 * 160 + 1
```

Thus `e * d` is congruent to `1` modulo `phi(n)`. Also, the message is in the valid range, `0 <= 99 < 187`.

## Encryption

RSA encryption uses the recipient's public key:

```text
c = m^e mod n = 99^7 mod 187
```

Use repeated squaring. First:

```text
99^2 = 9801 = 52 * 187 + 77
99^2 mod 187 = 77
```

Square that remainder to get the fourth power:

```text
99^4 mod 187 = 77^2 mod 187
             = 5929 mod 187
             = 132
```

Since `7 = 4 + 2 + 1`:

```text
99^7 mod 187 = (99^4 * 99^2 * 99) mod 187
              = (132 * 77 * 99) mod 187
```

Reduce the products as we go:

```text
132 * 77 = 10164 = 54 * 187 + 66
66 * 99  = 6534  = 34 * 187 + 176
```

Therefore, the ciphertext is:

```text
c = 176
```

## Decryption Check

The recipient applies the private exponent to the ciphertext:

```text
m = c^d mod n = 176^23 mod 187
```

Repeated squaring gives:

```text
176^1  mod 187 = 176
176^2  mod 187 = 121
176^4  mod 187 = 55
176^8  mod 187 = 33
176^16 mod 187 = 154
```

Because `23 = 16 + 4 + 2 + 1`, multiply the corresponding remainders:

```text
176 * 121 = 21296 = 113 * 187 + 165
165 * 55  = 9075  = 48 * 187 + 99
99 * 154  = 15246 = 81 * 187 + 99
```

The decrypted plaintext is `99`, which matches the original message. This confirms that the supplied key pair works for this example.

## Key Handling and Uses

The recommended practice is to publish the public key and protect the private key. A public key can be shared, but its owner should be authenticated (for example, with a trusted certificate or verified fingerprint) so an attacker cannot substitute a different key. The private key must remain secret and should be stored with access controls; never send it to people who need to send you encrypted messages.

| Operation | Key used | What it does |
| --- | --- | --- |
| Encrypt a message for the key owner | Recipient's public key `(e, n)` | Protects confidentiality; only the matching private key should decrypt it. |
| Decrypt a message | Recipient's private key `(d, n)` | Recovers a message encrypted for that recipient. |
| Create a digital signature | Signer's private key `(d, n)` | Binds the signer to data and helps detect changes. |
| Verify a digital signature | Signer's public key `(e, n)` | Checks that the signature matches the data and the corresponding public key. |

For this exercise, encryption is `c = m^e mod n`, and decryption is `m = c^d mod n`. The signature row describes the other common use of a key pair. In real systems, signatures are made over a hash using a signature scheme; they are not a way to keep a message secret.

## Calculator Program

The accompanying [exercise3_rsa.py](exercise3_rsa.py) program accepts the values as command-line parameters, prints the repeated-squaring steps, calculates the ciphertext, and decrypts it as a round-trip check.

```bash
python3 exercise3_rsa.py --message 99 --modulus 187 --public-exponent 7 --private-exponent 23
```

For these values, it reports ciphertext `176`, decrypted plaintext `99`, and a passed round-trip check.

## Practical Note

These tiny values demonstrate the RSA calculation only; they are not secure. Real applications use well-vetted RSA implementations with secure padding, such as OAEP for encryption and PSS for signatures. RSA is commonly used to protect a symmetric key rather than to encrypt large messages directly.