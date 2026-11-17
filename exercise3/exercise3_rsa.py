import argparse


def modular_power_with_steps(base: int, exponent: int, modulus: int) -> int:
    powers = []
    power = 1
    residue = base % modulus

    while power <= exponent:
        powers.append((power, residue))
        power *= 2
        residue = (residue * residue) % modulus

    selected = [(power, residue) for power, residue in powers if exponent & power]
    result = 1

    print(f"Calculating {base}^{exponent} mod {modulus}:")
    for power, residue in powers:
        print(f"  {base}^{power} mod {modulus} = {residue}")
    for power, residue in selected:
        result = (result * residue) % modulus
        print(f"  Multiply by the 2^{power.bit_length() - 1} term: result = {result}")

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Encrypt a message with RSA and decrypt it for verification."
    )
    parser.add_argument("--message", type=int, required=True, help="integer plaintext")
    parser.add_argument("--modulus", type=int, required=True, help="RSA modulus n")
    parser.add_argument("--public-exponent", type=int, required=True, help="public exponent e")
    parser.add_argument("--private-exponent", type=int, required=True, help="private exponent d")
    args = parser.parse_args()

    message = args.message
    modulus = args.modulus
    public_exponent = args.public_exponent
    private_exponent = args.private_exponent

    if modulus <= 1:
        parser.error("--modulus must be greater than 1")
    if public_exponent <= 0 or private_exponent <= 0:
        parser.error("the exponents must be positive integers")
    if not 0 <= message < modulus:
        parser.error("--message must be between 0 and modulus - 1")

    print(f"n = {modulus}")
    print(f"Public key:  (e, n) = ({public_exponent}, {modulus})")
    print(f"Private key: (d, n) = ({private_exponent}, {modulus})\n")

    ciphertext = modular_power_with_steps(message, public_exponent, modulus)
    print(f"\nCiphertext: {ciphertext}\n")

    recovered_message = modular_power_with_steps(
        ciphertext, private_exponent, modulus
    )
    print(f"\nDecrypted plaintext: {recovered_message}")
    print(f"Round-trip check: {'passed' if recovered_message == message else 'FAILED'}")


if __name__ == "__main__":
    main()