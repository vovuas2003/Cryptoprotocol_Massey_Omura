import numpy as np
import galois

def main():
    run_example()

def run_example():
    p = 2
    n = 8
    print(f"Common parameters: p = {p}, n = {n}")
    Alice = Participant(p, n)
    Alice.generate_key()
    print(f"Alice's secret keys: ({Alice.key}, {Alice.key_inv})")
    Bob = Participant(p, n)
    Bob.generate_key()
    print(f"Bob's secret keys: ({Bob.key}, {Bob.key_inv})")
    print()
    import random
    message = random.randint(0, p**n - 1)
    print("Alice: original message =", message)
    message = Alice.encrypt(message)
    print("Alice to Bob: encrypted message =", message)
    message = Bob.encrypt(message)
    print("Bob to Alice: double encrypted message =", message)
    message = Alice.decrypt(message)
    print("Alice to Bob: encrypted message =", message)
    message = Bob.decrypt(message)
    print("Bob: recovered message =", message)

class Participant():
    def __init__(self, p, n):
        self.n = n
        self.p = p
        try:
            self.field = galois.GF(p, n)
        except LookupError:
            irr_poly = galois.irreducible_poly(p, n)
            self.field = galois.GF(p, n, irreducible_poly = irr_poly, primitive_element = galois.primitive_element(irr_poly))
        except:
            print("Unexpected error!")
            raise
        self.poly_to_check_gcd = galois.Poly([1 for _ in range(self.n)], field = self.field)
        self.N_1 = self.p**self.n - 1
    def generate_key(self):
        while True:
            self.key = self.field.Random(1)[0]
            if self.key == self.field(0):
                continue
            if self.key == self.field(1):
                continue
            if self.check_gcd() == self.field(1):
                continue
            self.key = int(self.key)
            try:
                self.key_inv = pow(self.key, -1, self.N_1)
                break
            except:
                continue
    def check_gcd(self):
        return galois.gcd(galois.Poly(self.key.vector()[0], field = self.field), self.poly_to_check_gcd)
    def encrypt(self, message):
        return self.field(message) ** self.key
    def decrypt(self, message):
        return self.field(message) ** self.key_inv

if __name__ == "__main__":
    main()
