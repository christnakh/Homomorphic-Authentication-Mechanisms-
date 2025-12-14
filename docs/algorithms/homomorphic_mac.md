# Homomorphic Message Authentication Code (HMAC) Algorithms

This document provides detailed explanations of the homomorphic MAC algorithms implemented in this project.

## 1. Additive Homomorphic MAC

### Overview
Additive HMAC allows addition of authenticated messages: `MAC(m1) + MAC(m2) = MAC(m1 + m2)`.

### How It Works

**Key Generation:**
- Generate secret key: `k` (shared between clients and server)

**Tag Generation:**
- For message `m` with identifier `id`:
- Compute: `tag = H(k || id) · m` (in some group)
- Or: `tag = PRF(k, id) · m mod p`

**Verification:**
- Recompute expected tag: `tag' = H(k || id) · m`
- Check: `tag == tag'`

**Additive Combination:**
- For messages `m1, m2` with tags `tag1, tag2`:
- Combined message: `m_comb = m1 + m2`
- Combined tag: `tag_comb = tag1 + tag2`
- Verification: `tag_comb = H(k || id) · m_comb`

### Services Provided
- **Additive Homomorphism**: Tags can be added together
- **Fast Computation**: Symmetric operations (no pairing)
- **Compact Tags**: Small tag size (32 bytes)

### Strengths
- Very fast (symmetric cryptography)
- Small tag size
- Simple implementation
- Efficient for FL aggregation (additive updates)

### Limitations
- **No Public Verifiability**: Requires secret key
- **Key Distribution**: Secret key must be shared securely
- **Limited to Addition**: Only supports additive operations
- **Security Model**: Requires trusted server or key distribution

### Implementation
- **Type**: Custom implementation
- **Reference**: Based on additive homomorphic MAC constructions

### Security Properties
- **Security Notion**: Unforgeability under chosen message attacks
- **Assumption**: PRF security
- **Adversarial Model**: Resistant to forgery, but requires secret key management

### Use Case in FL
- Ideal when server is trusted and key distribution is feasible
- Efficient for many clients with additive aggregation
- Lower communication overhead than signatures

---

## 2. Linear Homomorphic MAC

### Overview
Linear HMAC supports linear combinations: `MAC(Σ αi·mi) = Σ αi·MAC(mi)`.

### How It Works

**Key Generation:**
- Generate secret key vector: `k = (k1, k2, ..., kn)`

**Tag Generation:**
- For vector `v = (v1, v2, ..., vn)` with identifier `id`:
- Compute: `tag = Σ ki · vi mod p`
- Or: `tag = PRF(k, id) · v mod p` (dot product)

**Verification:**
- Recompute: `tag' = Σ ki · vi mod p`
- Check: `tag == tag'`

**Linear Combination:**
- For vectors `v1, v2, ...` with tags `tag1, tag2, ...` and coefficients `α1, α2, ...`:
- Combined vector: `v_comb = Σ αi · vi`
- Combined tag: `tag_comb = Σ αi · tagi`
- Verification: `tag_comb = Σ ki · v_comb_i mod p`

### Services Provided
- **Linear Homomorphism**: Supports weighted linear combinations
- **Vector Authentication**: Authenticate multi-dimensional vectors
- **Flexible Aggregation**: Different weights for different clients

### Strengths
- More flexible than additive (supports coefficients)
- Fast symmetric operations
- Ideal for FL with weighted aggregation (FedAvg)
- Supports vector operations directly

### Limitations
- **No Public Verifiability**: Requires secret key
- **Key Distribution**: Secret key sharing needed
- **Limited to Linear**: Only linear operations supported
- **Vector Dimension**: Tag computation depends on vector size

### Implementation
- **Type**: Custom implementation
- **Reference**: Based on linear homomorphic MAC constructions

### Security Properties
- **Security Notion**: Unforgeability under linear combination attacks
- **Assumption**: PRF/LWE security
- **Adversarial Model**: Resistant to forgery of linear combinations

### Use Case in FL
- Perfect for FedAvg with different client weights
- Efficient for high-dimensional model updates
- Lower overhead than signatures for many clients

---

## 3. Polynomial-based Homomorphic MAC

### Overview
Polynomial HMAC supports polynomial operations on authenticated data.

### How It Works

**Key Generation:**
- Generate secret key: `k`

**Tag Generation:**
- For message `m` with identifier `id`:
- Evaluate polynomial: `P(x) = a0 + a1·x + a2·x² + ...`
- Compute: `tag = P(m)` where coefficients derived from `PRF(k, id)`

**Verification:**
- Recompute polynomial evaluation
- Check: `tag == P(m)`

**Polynomial Combination:**
- Combine tags using polynomial operations
- More expressive than linear operations

### Services Provided
- **Polynomial Homomorphism**: Supports polynomial operations
- **More Expressive**: Beyond linear operations
- **Flexible**: Can encode various operations

### Strengths
- More expressive than linear operations
- Can encode complex relationships
- Still uses symmetric cryptography (fast)

### Limitations
- **Higher Computational Cost**: Polynomial evaluation is expensive
- **Limited Polynomial Degree**: Security degrades with high degree
- **No Public Verifiability**: Requires secret key
- **Complex Key Management**: More complex than linear schemes

### Implementation
- **Type**: Custom implementation
- **Reference**: Based on polynomial evaluation MACs

### Security Properties
- **Security Notion**: Unforgeability under polynomial evaluation
- **Assumption**: PRF security
- **Adversarial Model**: Resistant to polynomial forgery attacks

### Use Case in FL
- Useful for non-linear aggregation schemes
- Experimental applications
- Less common in practice

---

## 4. Lattice-based Homomorphic MAC

### Overview
Lattice-based HMAC uses lattice cryptography for homomorphic authentication.

### How It Works

**Key Generation:**
- Generate secret lattice vector: `s ∈ Z_q^n`

**Tag Generation:**
- For message `m` (encoded as vector):
- Compute: `tag = s · m mod q` (dot product in lattice)
- Or: `tag = A·s + e + m mod q` where `A` is public matrix, `e` is error

**Verification:**
- Recompute tag using secret key
- Check: `tag == s · m mod q`

**Lattice Combination:**
- Combine tags using lattice operations
- Supports various homomorphic operations

### Services Provided
- **Lattice-based Security**: Post-quantum potential
- **Homomorphic Operations**: Various operations supported
- **Vector Operations**: Natural for vector authentication

### Strengths
- **Post-Quantum Security**: Based on lattice problems (LWE/SIS)
- **Flexible**: Supports various operations
- **Future-Proof**: Quantum-resistant potential

### Limitations
- **Larger Parameters**: Requires larger key sizes
- **Higher Computational Cost**: Lattice operations are expensive
- **No Public Verifiability**: Requires secret key
- **Less Mature**: Less studied than classical schemes

### Implementation
- **Type**: Custom implementation (simplified)
- **Reference**: Based on LWE-based MAC constructions

### Security Properties
- **Security Notion**: Unforgeability under LWE assumption
- **Assumption**: Learning With Errors (LWE) or Short Integer Solution (SIS)
- **Adversarial Model**: Resistant to quantum attacks (theoretically)

### Use Case in FL
- Future-proof solution for quantum computing era
- Experimental applications
- When post-quantum security is required

---

## Comparison Summary

| Algorithm | Tag Size | Key Size | Homomorphic Op | Public Verify | Speed |
|-----------|----------|----------|----------------|---------------|-------|
| Additive HMAC | 32 bytes | 32 bytes | Addition | No | Very Fast |
| Linear HMAC | 32 bytes | 32 bytes | Linear | No | Very Fast |
| Polynomial HMAC | 32 bytes | 32 bytes | Polynomial | No | Fast |
| Lattice HMAC | 32 bytes | 256+ bytes | Various | No | Moderate |

## Key Differences from Digital Signatures

1. **Symmetric vs Asymmetric**: MACs use shared secrets, signatures use public keys
2. **Public Verifiability**: Signatures allow public verification, MACs require secret key
3. **Key Distribution**: MACs need secure key distribution, signatures use public keys
4. **Performance**: MACs are generally faster (symmetric operations)
5. **Use Cases**: MACs for trusted environments, signatures for public verifiability

## Trade-offs in FL Context

### When to Use HMAC:
- Server is trusted
- Key distribution is feasible
- Performance is critical
- Public verifiability not required
- Many clients (low overhead per client)

### When to Use Digital Signatures:
- Public verifiability required
- Server may be untrusted
- Auditability needed
- Key distribution is difficult
- Regulatory compliance requires signatures

