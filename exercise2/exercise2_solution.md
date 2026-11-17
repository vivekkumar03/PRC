# Exercise 2: One round of AES-128

The plaintext is `buy me some potato chips please` and the key is
`keys are boring1`. Both are encoded as ASCII/UTF-8; the 16-byte key therefore
selects AES-128. The first 16-byte plaintext block is `buy me some pota`.
No padding is needed for this first block. The remaining 15 bytes would need
padding if a block mode requiring full blocks were used; for example, PKCS#7
adds one byte `01`.

All numbers below are hexadecimal. Each four-byte **column** of the matrix
is filled in order from the byte stream, as specified by AES. The AES
algorithm performs an initial AddRoundKey **before** round 1. This is included
here; the result shown is the state after one round, **not** a complete AES
ciphertext.

## Input and initial AddRoundKey

```text
First plaintext block (hex):
62 75 79 20 6d 65 20 73 6f 6d 65 20 70 6f 74 61

State                      Key (round 0)
62 6d 6f 70                6b 20 20 69
75 65 6d 6f                65 61 62 6e
79 20 65 74                79 72 6f 67
20 73 20 61                73 65 72 31

Initial AddRoundKey = State XOR Key
09 4d 4f 19
10 04 0f 01
00 52 0a 13
53 16 52 50
```

For example, the top-left entry is `62 XOR 6b = 09`.

## Round 1 key expansion

Split the original key into four words:

```text
w0 = 6b657973   w1 = 20617265   w2 = 20626f72   w3 = 696e6731
RotWord(w3) = 6e673169
SubWord(...) = 9f85c7f9
Rcon[1] = 01000000
g(w3) = 9e85c7f9
w4 = w0 XOR g(w3) = f5e0be8a
w5 = w1 XOR w4    = d581ccef
w6 = w2 XOR w5    = f5e3a39d
w7 = w3 XOR w6    = 9c8dc4ac
```

These words form the round 1 key, arranged in columns:

```text
f5 d5 f5 9c
e0 81 e3 8d
be cc a3 c4
8a ef 9d ac
```

## Round 1 transformations

**SubBytes:** apply the AES S-box to each byte. For example, `S(09) = 01`.

```text
01 e3 84 d4
ca f2 76 7c
63 00 67 7d
ed 47 00 53
```

**ShiftRows:** rotate rows 0, 1, 2 and 3 left by 0, 1, 2 and 3 positions.

```text
01 e3 84 d4
f2 76 7c ca
67 7d 63 00
53 ed 47 00
```

**MixColumns:** multiply each column by the AES matrix in the field
GF(2^8), using the reduction polynomial `x^8 + x^4 + x^3 + x + 1`:

```text
02 03 01 01
01 02 03 01
01 01 02 03
03 01 01 02
```

For the first output byte, `02·01 XOR 03·f2 XOR 67 XOR 53 = 3b`;
field multiplication gives `03·f2 = 0d`. Applying this to all columns:

```text
3b d7 b3 f6
04 65 9e 5b
c8 43 f7 1e
30 f4 06 ad
```

**AddRoundKey:** XOR with the round 1 key:

```text
ce 02 46 6a
e4 e4 7d d6
76 8f 54 da
ba 1b 9b 01
```

Reading columns in order, the **one-round state** is:

```text
ce e4 76 ba 02 e4 8f 1b 46 7d 54 9b 6a d6 da 01
```

## Check and interpretation

The implementation used for the calculation was checked against the NIST
AES-128 test vector and against a complete AES-128-ECB encryption using
OpenSSL via Node.js. The full encryption of this one block, used only as a
check, is `f3d7e0fa0d0892f0ac7938e0d76629ff`; it is not the one-round
answer. Real encryption requires all AES rounds and a suitable authenticated
mode such as AES-GCM; ECB is used only for this single-block check.

Source: [NIST FIPS 197: Advanced Encryption Standard](https://csrc.nist.gov/pubs/fips/197/final).
