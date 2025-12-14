# Mathematical Foundations of Homomorphic Authentication

This document explains the **real mathematical homomorphic properties** implemented in this project. These are not simple hashing schemes—they are cryptographically secure constructions based on hard mathematical problems.

## Table of Contents
1. [Overview](#overview)
2. [Homomorphic MACs](#homomorphic-macs)
3. [Homomorphic Signatures](#homomorphic-signatures)
4. [Security Foundations](#security-foundations)
5. [Cryptographic Operations](#cryptographic-operations)

---

## Overview

### What is Homomorphic Authentication?

Homomorphic authentication allows operations on authenticated data while maintaining authenticity:

- **Traditional MAC**: Can only verify exact message
- **Homomorphic MAC**: Can verify *operations* on messages

**Example**: If you have authenticated tags for `m₁` and `m₂`, you can compute a valid tag for `m₁ + m₂` without the secret key!

### Why Not Just Hashing?

❌ **Simple hashing** (SHA256, etc.):
- `hash(m1) + hash(m2) ≠ hash(m1 + m2)`
- No algebraic structure
- Cannot verify operations on data

✅ **Homomorphic schemes**:
- Use algebraic structures (groups, rings, fields)
- Tags preserve mathematical relationships
- Based on hard cryptographic problems

---

## Homomorphic MACs

### 1. Additive HMAC

**Mathematical Construction**:
```
Tag generation: t = F_k(id) · m mod p
where:
  F_k(id) = PRF output (AES or SHA256)
  m = message as integer
  p = large prime (2^256 - 189)
```

**Homomorphic Property**:
```
t₁ + t₂ mod p = F_k(id₁)·m₁ + F_k(id₂)·m₂ mod p
              = valid tag for combined message
```

**Security**:
- Based on PRF (Pseudorandom Function) security
- AES or SHA256 as PRF
- Security holds if PRF is indistinguishable from random

**Implementation Details**:
```python
# Prime field Z_p
p = 2**256 - 189  # 256-bit prime

# PRF using AES-ECB
F_k(id) = AES_k(id) mod p

# Tag generation
prf_value = F_k(identifier)
msg_int = hash(message)
tag = (prf_value * msg_int) mod p

# Homomorphic addition
tag_combined = (tag1 + tag2 + ... + tag_n) mod p
```

---

### 2. Linear HMAC

**Mathematical Construction**:
```
Tag for vector v: t = ⟨F_k(id), v⟩ mod p
where:
  F_k(id) = (r₁, r₂, ..., rₙ) ∈ Z_p^n (PRF output vector)
  v = (v₁, v₂, ..., vₙ) ∈ Z_p^n (message vector)
  ⟨·,·⟩ = inner product
```

**Homomorphic Property**:
```
For linear combination: v = c₁·v₁ + c₂·v₂
Combined tag: t = c₁·t₁ + c₂·t₂ mod p
This is a valid tag for v!
```

**Security**:
- Based on PRF security
- Inner product in finite field Z_p
- Supports arbitrary linear combinations

**Use Case**: Federated Learning
```python
# Three clients compute gradients
gradient1 = [0.5, 0.3, 0.2, ...]  # Client 1
gradient2 = [0.4, 0.6, 0.1, ...]  # Client 2
gradient3 = [0.3, 0.4, 0.3, ...]  # Client 3

# Each client authenticates their gradient
tag1 = mac.generate_tag(gradient1, id="client1")
tag2 = mac.generate_tag(gradient2, id="client2")
tag3 = mac.generate_tag(gradient3, id="client3")

# Server aggregates (e.g., weighted average)
weights = [0.3, 0.5, 0.2]
aggregated_gradient = 0.3*g1 + 0.5*g2 + 0.2*g3

# Server computes aggregated tag (no secret key needed!)
aggregated_tag = 0.3*t1 + 0.5*t2 + 0.2*t3 mod p

# Central authority verifies aggregated result
verify(aggregated_gradient, aggregated_tag)  # ✓ Valid!
```

---

### 3. Polynomial HMAC

**Mathematical Construction**:
```
Secret polynomial: P(x) = a₀ + a₁·x + a₂·x² + ... + aₐ·xᵈ in Z_p[x]
Tag: t = P(H(m)) · F_k(id) mod p
```

**Homomorphic Property**:
- Polynomial operations on tags
- t₁ · t₂ corresponds to multiplicative operations

**Security**:
- Based on polynomial evaluation
- Coefficients derived from secret key via PRF

---

### 4. Lattice HMAC (Post-Quantum)

**Mathematical Construction** (LWE-based):
```
Key generation:
  Secret key: s ∈ Z_q^n (small coefficients)
  Public matrix: A ∈ Z_q^(m×n) (random)

Tag generation:
  t = A·s + e + m·h mod q
where:
  e = small error from discrete Gaussian
  h = hash of identifier (lattice vector)
  m = message scalar
```

**Homomorphic Property**:
```
Additive: t₁ + t₂ = A·s + e₁ + m₁·h + A·s + e₂ + m₂·h
                  = A·(2s) + (e₁+e₂) + (m₁+m₂)·h
                  ≈ valid tag for (m₁+m₂)
```

**Security**:
- **Learning With Errors (LWE)** problem
- Believed to be **quantum-resistant**
- Error term ensures computational hardness

**Why Post-Quantum?**
- Classical schemes (RSA, elliptic curves) vulnerable to Shor's algorithm on quantum computers
- LWE remains hard even for quantum computers
- Future-proof security

---

## Homomorphic Signatures

### 1. BLS Signatures (Boneh-Lynn-Shacham)

**Mathematical Construction** (Pairing-based):
```
Groups: G₁, G₂, G_T with bilinear pairing e: G₁ × G₂ → G_T

Key generation:
  Private key: sk ∈ Z_p (random scalar)
  Public key: pk = sk · G₂ ∈ G₂

Signing:
  σ = sk · H(m) where H: {0,1}* → G₁

Verification:
  e(σ, G₂) == e(H(m), pk)
```

**Homomorphic Property - Signature Aggregation**:
```
Multiple signatures σ₁, σ₂, ..., σₙ on different messages

Aggregate: σ_agg = σ₁ + σ₂ + ... + σₙ (elliptic curve point addition)

Verify: e(σ_agg, G₂) == ∏ e(H(mᵢ), pkᵢ)
```

**Key Benefit**: Constant signature size!
- Individual signatures: 96 bytes each (n × 96 bytes total)
- Aggregated signature: 96 bytes (regardless of n!)

**Security**:
- Computational Diffie-Hellman (CDH) in Gap groups
- Pairing-based cryptography
- Used in blockchain (Ethereum 2.0, Chia)

**Implementation**: Uses `blspy` library (BLS12-381 curve)

---

### 2. RSA Signatures (Multiplicative Homomorphism)

**Mathematical Construction**:
```
Key generation:
  Choose primes p, q
  N = p·q
  e, d such that e·d ≡ 1 (mod φ(N))

Textbook RSA signing:
  σ = m^d mod N

Verification:
  σ^e mod N == m
```

**Homomorphic Property - Multiplicative**:
```
σ₁ = m₁^d mod N
σ₂ = m₂^d mod N

σ₁ · σ₂ mod N = (m₁^d · m₂^d) mod N
              = (m₁ · m₂)^d mod N
              = sign(m₁ · m₂)
```

**Security Note**:
- ⚠️ Textbook RSA is **insecure** (existential forgery)
- Secure RSA uses padding (PKCS#1, PSS) which **breaks homomorphism**
- Our implementation offers both modes:
  - `homomorphic_mode=True`: Demonstrates mathematical property (insecure)
  - `homomorphic_mode=False`: Secure RSA with padding (no homomorphism)

**Use Case**: Demonstration of multiplicative homomorphism concept

---

### 3. Waters Homomorphic Signatures

**Mathematical Construction** (Pairing-based):
```
Key generation:
  α ∈ Z_p (private key)
  g^α ∈ G (public key)
  u₁, u₂, ..., uₙ ∈ G (public parameters)

Signing vector v = (v₁, v₂, ..., vₙ):
  σ = (g^α · H(id) · ∏ uᵢ^vᵢ)^r
where r is random

Verification:
  e(σ, g^r) == e(g^α · H(id) · ∏ uᵢ^vᵢ, g)
```

**Homomorphic Property - Linear Combinations**:
```
If σᵢ is signature on vector vᵢ, then:

σ = ∏ σᵢ^cᵢ is valid signature on v = ∑ cᵢ·vᵢ
```

**Security**:
- CDH assumption in bilinear groups
- Supports verification of linear combinations
- Perfect for federated learning!

**Implementation**: Uses `petlib` for elliptic curve operations

---

### 4. Boneh-Boyen Signatures

**Mathematical Construction**:
```
Key generation:
  x ∈ Z_p (private key)
  g^x ∈ G (public key)

Signing:
  σ = g^(1/(x + H(m))) ∈ G

Verification (using pairing):
  e(σ, g^x · g^H(m)) == e(g, g)
```

**Homomorphic Property - Aggregation**:
```
Multiple signatures can be aggregated:
σ_agg = ∏ σᵢ (group multiplication)
```

**Security**:
- q-Strong Diffie-Hellman (q-SDH) assumption
- Short signatures without random oracles

---

## Security Foundations

### Cryptographic Hardness Assumptions

| Scheme | Hardness Assumption | Quantum Safe? |
|--------|-------------------|---------------|
| Additive HMAC | PRF security (AES/SHA256) | ❌ No* |
| Linear HMAC | PRF security | ❌ No* |
| Polynomial HMAC | Polynomial evaluation | ❌ No* |
| **Lattice HMAC** | **LWE problem** | **✅ Yes** |
| BLS Signatures | CDH in pairing groups | ❌ No |
| RSA Signatures | RSA problem | ❌ No |
| Waters Signatures | CDH in bilinear groups | ❌ No |
| Boneh-Boyen | q-SDH assumption | ❌ No |

*Note: Symmetric schemes (MACs) require longer keys for quantum resistance (256-bit keys)

### Security Properties

1. **Unforgeability**: Cannot create valid tags without secret key
2. **Collision Resistance**: Hard to find two messages with same tag
3. **Homomorphic Correctness**: Operations preserve validity
4. **Security under Composition**: Multiple operations don't weaken security

---

## Cryptographic Operations

### Finite Field Arithmetic

**Prime Field Z_p** (p = 2^256 - 189):
```python
# Addition
(a + b) mod p

# Multiplication
(a · b) mod p

# Inverse
a^(-1) mod p using Extended Euclidean Algorithm
```

### Elliptic Curve Operations (with petlib)

**Curve**: NIST P-256 or BLS12-381

```python
# Point addition
P + Q

# Scalar multiplication
k · P

# Pairing (for BLS)
e(P, Q) where P ∈ G₁, Q ∈ G₂
```

### Lattice Operations

**Vector Operations in Z_q^n**:
```python
# Matrix-vector multiplication
A · s mod q

# Vector addition
v₁ + v₂ mod q

# Gaussian sampling (for LWE error)
e ← D_{Z^n, σ} (discrete Gaussian)
```

---

## Performance Characteristics

| Scheme | Tag Size | Key Gen | Tag Gen | Verification | Homomorphic Op |
|--------|----------|---------|---------|--------------|----------------|
| Additive HMAC | 32 bytes | Fast | Fast | Fast | Very Fast |
| Linear HMAC | 32 bytes | Medium | Medium | Medium | Fast |
| BLS | 96 bytes | Medium | Medium | Slow (pairing) | Fast |
| RSA | 256 bytes | Slow | Slow | Fast | Medium |
| Lattice | 32 bytes | Fast | Medium | Medium | Fast |

**Legend**:
- Fast: < 1ms
- Medium: 1-10ms
- Slow: > 10ms

---

## Practical Applications

### 1. Federated Learning
```
Clients compute local updates → authenticate with Linear HMAC
Server aggregates encrypted updates → tags combine homomorphically
Central authority verifies aggregated result
```

### 2. Blockchain Aggregation
```
Multiple transactions → sign with BLS
Aggregate signatures → constant size proof
Verify entire block with single pairing check
```

### 3. Network Coding
```
Network nodes combine packets → additive HMAC
Receiver verifies combined packets
Detects malicious modifications by intermediate nodes
```

### 4. Post-Quantum Security
```
Use Lattice HMAC for quantum-resistant authentication
Future-proof against quantum attacks
Critical for long-term data protection
```

---

## Comparison with Simple Hashing

| Feature | Simple Hash (SHA256) | Homomorphic Auth |
|---------|---------------------|------------------|
| **Verification** | ✓ Can verify exact message | ✓ Can verify exact message |
| **Operations** | ✗ Cannot verify operations | ✓ **Can verify operations on data** |
| **Example** | hash(m₁+m₂) ≠ hash(m₁) + hash(m₂) | tag(m₁+m₂) = tag(m₁) + tag(m₂) |
| **Algebraic Structure** | ✗ None | ✓ Group/Ring/Field structure |
| **Security** | Collision resistance | PRF/CDH/LWE hardness |
| **Key Required** | ✗ No | ✓ Yes (secret key) |

**The Key Difference**:
- **Hashing**: No algebraic structure → cannot verify operations
- **Homomorphic**: Preserves algebraic structure → can verify f(m₁, m₂) from tags of m₁, m₂

---

## References

### Papers
1. Boneh, D., & Freeman, D. (2011). "Homomorphic Signatures for Polynomial Functions"
2. Agrawal, S., & Boneh, D. (2009). "Homomorphic MACs: MAC-based Integrity for Network Coding"
3. Boneh, D., Lynn, B., & Shacham, H. (2001). "Short Signatures from the Weil Pairing"
4. Waters, B. (2005). "Efficient Identity-Based Encryption Without Random Oracles"
5. Regev, O. (2005). "On Lattices, Learning with Errors, and Cryptography"

### Libraries Used
- **blspy**: BLS signatures (BLS12-381 pairing curve)
- **petlib**: Elliptic curve operations with pairings
- **pycryptodome**: AES and RSA implementations
- **cryptography**: EdDSA (Ed25519)
- **tenseal**: Homomorphic encryption (Microsoft SEAL wrapper)

### Standards
- NIST SP 800-186: Elliptic Curve Cryptography
- BLS12-381: Pairing-friendly curve (used in Ethereum 2.0)
- FIPS 186-4: Digital Signature Standard

---

## Conclusion

This project implements **real cryptographic homomorphism**, not simple hashing:

✅ **Mathematical foundations**: Group theory, finite fields, elliptic curves, lattices
✅ **Security**: Based on hard problems (CDH, RSA, LWE)
✅ **Practical**: Tested and verified homomorphic properties
✅ **Post-quantum**: Lattice-based schemes for quantum resistance

The implementations demonstrate that operations on authenticated data can be verified without revealing the secret key—a powerful property for distributed systems, blockchain, and privacy-preserving machine learning!

