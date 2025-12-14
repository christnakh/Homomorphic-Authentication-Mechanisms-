# Homomorphic Digital Signature Algorithms

This document provides detailed explanations of the homomorphic digital signature algorithms implemented in this project.

## 1. BLS (Boneh-Lynn-Shacham) Aggregate Signatures

### Overview
BLS signatures are a pairing-based aggregate signature scheme that allows multiple signatures to be combined into a single compact signature.

### How It Works

**Key Generation:**
- Generate a private key: `sk ∈ Z_q` (random element in prime field)
- Compute public key: `pk = g^sk` where `g` is a generator of group G1

**Signing:**
- Hash message: `H(m) ∈ G2`
- Compute signature: `σ = H(m)^sk ∈ G2`

**Verification:**
- Check: `e(σ, g) = e(H(m), pk)` using bilinear pairing

**Aggregation:**
- Multiple signatures can be aggregated: `σ_agg = σ1 · σ2 · ... · σn`
- Verification: `e(σ_agg, g) = ∏ e(H(m_i), pk_i)`

### Services Provided
- **Public Verifiability**: Anyone can verify signatures with public keys
- **Aggregation**: Multiple signatures combine into one compact signature
- **Homomorphic Property**: Aggregate(sig1, sig2) = sig1 · sig2

### Strengths
- Compact aggregate signatures (single group element, ~96 bytes)
- Efficient aggregation (multiplication in group)
- Strong security guarantees (EUF-CMA under co-CDH)
- Public verifiability without secret keys

### Limitations
- Requires pairing operations (computationally expensive)
- Larger public keys (~48 bytes per client)
- Requires bilinear groups (special elliptic curves)

### Open-Source Implementation
- **Library**: `blspy` (Chia Network)
- **Link**: https://github.com/Chia-Network/blspy
- **License**: Apache 2.0

### Security Properties
- **Security Notion**: EUF-CMA (Existential Unforgeability under Chosen Message Attacks)
- **Assumption**: Co-Computational Diffie-Hellman (co-CDH) in bilinear groups
- **Adversarial Model**: Resistant to rogue-key attacks with proper key registration

---

## 2. Linearly Homomorphic Signatures (LHS)

### Overview
LHS allows verification of linear combinations of signed vectors without revealing individual signatures.

### How It Works

**Key Generation:**
- Generate master secret key: `msk`
- Derive public key: `pk = f(msk)`

**Signing a Vector:**
- For vector `v = (v1, v2, ..., vn)` with message ID `id`:
- Compute: `σ = Sign(msk, id, v)`
- Signature encodes linear structure

**Linear Combination:**
- Given signed vectors `(v1, σ1), (v2, σ2), ...` and coefficients `α1, α2, ...`
- Combined vector: `v_comb = Σ αi · vi`
- Combined signature: `σ_comb = Combine(σ1, σ2, ..., α1, α2, ...)`

**Verification:**
- Verify: `Verify(pk, id, v_comb, σ_comb)` checks that `v_comb` is valid linear combination

### Services Provided
- **Linear Homomorphism**: Verify linear operations on authenticated data
- **Public Verifiability**: Public key verification
- **Vector Authentication**: Authenticate multi-dimensional data

### Strengths
- Supports arbitrary linear combinations
- Useful for FL where updates are aggregated linearly
- Public verifiability

### Limitations
- Limited to linear operations only
- Larger signature size (depends on vector dimension)
- More complex key management

### Implementation
- **Type**: Custom implementation based on bilinear group constructions
- **Reference**: Based on Catalano-Fiore linearly homomorphic signatures

### Security Properties
- **Security Notion**: EUF-CMA for linear combinations
- **Assumption**: Discrete logarithm in bilinear groups
- **Adversarial Model**: Resistant to forgery of linear combinations

---

## 3. RSA-based Homomorphic Signatures

### Overview
RSA signatures with multiplicative homomorphic properties.

### How It Works

**Key Generation:**
- Generate RSA key pair: `(n, e, d)` where `n = p·q`
- Public key: `(n, e)`, Private key: `d`

**Signing:**
- Hash message: `h = H(m)`
- Signature: `σ = h^d mod n`

**Verification:**
- Check: `σ^e mod n = H(m)`

**Multiplicative Homomorphism:**
- For messages `m1, m2`: `σ(m1) · σ(m2) = σ(m1 · m2) mod n`
- This allows multiplication of signed values

### Services Provided
- **Multiplicative Homomorphism**: Product of signatures equals signature of product
- **Public Verifiability**: Standard RSA verification
- **Widely Deployed**: RSA is well-understood and standardized

### Strengths
- Simple and well-understood
- Standard RSA security
- Can be adapted for additive homomorphism with encoding

### Limitations
- Only multiplicative homomorphism (not additive)
- Large key sizes (2048+ bits)
- Slower than elliptic curve schemes
- Not ideal for FL aggregation (which is additive)

### Open-Source Implementation
- **Library**: `pycryptodome`
- **Link**: https://github.com/Legrandin/pycryptodome
- **License**: Public Domain / BSD

### Security Properties
- **Security Notion**: EUF-CMA
- **Assumption**: RSA problem (factoring)
- **Adversarial Model**: Standard RSA security model

---

## 4. EdDSA with Aggregation

### Overview
EdDSA (Edwards-curve Digital Signature Algorithm) with custom aggregation support.

### How It Works

**Key Generation:**
- Generate private key: `sk` (random 32 bytes)
- Compute public key: `pk = sk · B` where `B` is base point

**Signing:**
- Compute: `R = r · B`, `s = r + H(R, pk, m) · sk`
- Signature: `(R, s)`

**Verification:**
- Check: `s · B = R + H(R, pk, m) · pk`

**Aggregation:**
- For EdDSA, aggregation requires concatenation or multi-signature protocol
- Multiple signatures can be verified together

### Services Provided
- **Fast Signing/Verification**: EdDSA is very efficient
- **Small Signatures**: 64 bytes
- **Small Keys**: 32-byte public keys
- **Aggregation Support**: Can aggregate multiple signatures

### Strengths
- Very fast (faster than RSA, comparable to ECDSA)
- Small signature and key sizes
- Deterministic (no randomness needed)
- Strong security (Ed25519 curve)

### Limitations
- Aggregation requires additional protocol (not native)
- Less efficient aggregation than BLS
- Public key distribution needed

### Open-Source Implementation
- **Library**: `cryptography` (Python)
- **Link**: https://github.com/pyca/cryptography
- **License**: Apache 2.0 / BSD

### Security Properties
- **Security Notion**: EUF-CMA
- **Assumption**: Discrete logarithm on Edwards curves
- **Adversarial Model**: Standard EdDSA security

---

## Comparison Summary

| Algorithm | Signature Size | Key Size | Aggregation | Public Verify | Homomorphic Op |
|-----------|---------------|----------|-------------|---------------|----------------|
| BLS | 96 bytes | 48 bytes | Native | Yes | Multiplicative |
| LHS | 32+ bytes | 32+ bytes | Linear | Yes | Linear |
| RSA | 256 bytes | 256 bytes | Custom | Yes | Multiplicative |
| EdDSA | 64 bytes | 32 bytes | Protocol | Yes | Limited |

