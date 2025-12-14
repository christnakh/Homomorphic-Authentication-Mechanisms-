# Non-Homomorphic Signature Schemes as Alternatives

## Overview

This document explains how **RSA** and **EdDSA** (non-homomorphic signature schemes) serve as alternatives and baselines for comparison with homomorphic authentication schemes in Federated Learning.

## Why Include Non-Homomorphic Schemes?

### 1. Baseline Comparison

Non-homomorphic schemes provide a **well-understood baseline** for comparing the performance and overhead of homomorphic properties:

- **Performance Baseline**: Shows the computational cost of homomorphic operations
- **Communication Baseline**: Demonstrates communication overhead of aggregation
- **Security Baseline**: Provides standard security guarantees for comparison

### 2. Practical Alternatives

In certain FL scenarios, non-homomorphic schemes may be **preferable**:

- **Small-Scale FL**: With few clients (<10), individual verification is acceptable
- **Individual Audit Requirements**: When each client's update must be verified separately
- **No Aggregation Needed**: When aggregation is not required or done differently
- **Standard Compliance**: When regulatory requirements mandate standard signatures

## RSA Signature Scheme

### Implementation Details

**Open-Source Library**: `pycryptodome`
**Link**: https://github.com/Legrandin/pycryptodome

**How It Works**:
1. **Key Generation**: Generate RSA key pair (n, e, d) where n = p·q
2. **Signing**: Hash message with SHA-256, then sign: `σ = H(m)^d mod n`
3. **Verification**: Verify: `σ^e mod n = H(m)`
4. **Aggregation**: **NOT SUPPORTED** - Each signature must be verified individually

**Code Implementation**:
```python
from src.algorithms.homomorphic_signatures import RSASignature

# Initialize
rsa = RSASignature(key_size=2048)

# Key generation
private_key, public_key = rsa.key_generation()

# Signing
message = b"model_update"
signature, sign_time = rsa.sign(message)

# Verification (individual)
is_valid, verify_time = rsa.verify(message, signature)

# Aggregation: NOT SUPPORTED
# Must verify each signature individually (O(n) operations)
```

### How RSA Serves as an Alternative

#### 1. Baseline for Performance Comparison

**Comparison with BLS (Homomorphic)**:
- **BLS**: Aggregate n signatures → 1 verification (O(1))
- **RSA**: Verify n signatures individually (O(n))
- **Overhead**: RSA shows the cost of non-homomorphic verification

**Example**:
- 100 clients with RSA: 100 individual verifications (~500-1000ms)
- 100 clients with BLS: 1 aggregate verification (~10-60ms)
- **Speedup**: ~10-100x with homomorphic scheme

#### 2. Small-Scale FL Scenarios

**When RSA is Suitable**:
- **Few Clients**: <10 clients where O(n) verification is acceptable
- **Low Frequency**: Infrequent updates where verification time is not critical
- **Individual Audit**: When each client's contribution must be verified separately

**Example Scenario**:
```
FL System: 5 clients, 1 update per day
- RSA: 5 verifications × 5ms = 25ms (acceptable)
- BLS: 1 aggregate verification = 10ms (overkill for small scale)
```

#### 3. Standard Compliance

**Regulatory Requirements**:
- Some regulations require standard digital signatures (RSA, ECDSA)
- Homomorphic schemes may not be approved for certain use cases
- RSA provides compliance while maintaining security

#### 4. No Aggregation Needed

**Scenarios**:
- **Sequential Processing**: When updates are processed one at a time
- **Selective Aggregation**: When only some updates are aggregated
- **Different Aggregation Methods**: When aggregation doesn't require homomorphic properties

### Limitations

1. **No Aggregation**: Cannot combine signatures efficiently
2. **O(n) Verification**: Linear time complexity for n clients
3. **Large Key Sizes**: 2048+ bit keys (larger than elliptic curve schemes)
4. **Slower Operations**: RSA operations are slower than elliptic curve schemes

## EdDSA Signature Scheme

### Implementation Details

**Open-Source Library**: `cryptography` (Python)
**Link**: https://github.com/pyca/cryptography

**How It Works**:
1. **Key Generation**: Generate Ed25519 key pair (sk, pk = sk·B)
2. **Signing**: Compute `R = r·B`, `s = r + H(R, pk, m)·sk`, signature = (R, s)
3. **Verification**: Check `s·B = R + H(R, pk, m)·pk`
4. **Aggregation**: **Concatenation Only** - Not true homomorphic aggregation

**Code Implementation**:
```python
from src.algorithms.homomorphic_signatures import EdDSASignature

# Initialize
eddsa = EdDSASignature()

# Key generation
private_key, public_key = eddsa.key_generation()

# Signing
message = b"model_update"
signature, sign_time = eddsa.sign(message)

# Verification
is_valid, verify_time = eddsa.verify(message, signature, public_key)

# Aggregation: Concatenation (not true homomorphic)
signatures = [sig1, sig2, ..., sign]
aggregated, _ = eddsa.aggregate_signatures(signatures)
# Verification still requires O(n) operations
```

### How EdDSA Serves as an Alternative

#### 1. Performance Comparison

**Speed Comparison**:
- **EdDSA**: Very fast signing/verification (~0.1-1ms per operation)
- **BLS**: Slower due to pairing operations (~1-10ms per operation)
- **Trade-off**: EdDSA is faster but requires O(n) verification

**Example**:
- 10 clients with EdDSA: 10 verifications × 0.5ms = 5ms
- 10 clients with BLS: 1 aggregate verification = 10ms
- **For small n**: EdDSA may be faster despite O(n) complexity

#### 2. Compact Signatures

**Size Comparison**:
- **EdDSA**: 64 bytes per signature
- **BLS**: 96 bytes per signature
- **RSA**: 256 bytes per signature (2048-bit)

**Communication Overhead**:
- **EdDSA**: 10 clients × 64 bytes = 640 bytes
- **BLS**: 10 clients × 96 bytes = 960 bytes (but aggregates to 96 bytes)
- **For small n**: EdDSA has lower total communication

#### 3. Deterministic Signing

**Advantages**:
- **No Randomness**: EdDSA is deterministic (RFC 8032)
- **Reproducibility**: Same message + key = same signature
- **Simpler Implementation**: No need for secure random number generation during signing

#### 4. Resource-Constrained Environments

**When EdDSA is Suitable**:
- **IoT Devices**: Low-power devices benefit from fast EdDSA operations
- **Mobile Clients**: Battery-constrained devices
- **Real-Time Systems**: When latency is critical

### Limitations

1. **No True Aggregation**: Concatenation requires O(n) verification
2. **Scalability**: Performance degrades linearly with number of clients
3. **Not Homomorphic**: Cannot verify aggregated result directly

## Comparison Table

| Property | BLS (Homomorphic) | RSA (Non-Homomorphic) | EdDSA (Non-Homomorphic) |
|----------|-------------------|----------------------|-------------------------|
| **Aggregation** | ✅ True homomorphic | ❌ Not supported | ⚠️ Concatenation only |
| **Verification** | O(1) aggregate | O(n) individual | O(n) individual |
| **Signature Size** | 96 bytes | 256 bytes | 64 bytes |
| **Key Size** | 48 bytes | 256 bytes | 32 bytes |
| **Signing Speed** | ~1-5ms | ~5-10ms | ~0.1-1ms |
| **Verification Speed** | ~5-10ms (aggregate) | ~5-10ms (individual) | ~0.1-1ms (individual) |
| **Open Source** | ✅ blspy | ✅ pycryptodome | ✅ cryptography |
| **Best For** | Large-scale FL | Small-scale FL, compliance | Small-scale FL, speed |

## When to Use Each Scheme

### Use BLS (Homomorphic) When:
- ✅ Many clients (>10)
- ✅ Aggregation is required
- ✅ Communication overhead must be minimized
- ✅ O(1) verification is needed

### Use RSA (Non-Homomorphic) When:
- ✅ Few clients (<10)
- ✅ Standard compliance required
- ✅ Individual audit trails needed
- ✅ Regulatory approval required

### Use EdDSA (Non-Homomorphic) When:
- ✅ Few clients (<10)
- ✅ Speed is critical
- ✅ Resource-constrained environments
- ✅ Compact signatures needed

## Implementation in FL Pipeline

### Client-Side (Same for All Schemes)

```python
# All schemes use the same client interface
client = FLClient(
    client_id=1,
    auth_scheme="BLS"  # or "RSA" or "EdDSA"
)

# Prepare authenticated update
update_data = client.prepare_update(global_model)
# Returns: {update, signature, public_key, ...}
```

### Server-Side (Different Verification)

```python
# BLS: Homomorphic aggregation
if scheme == "BLS":
    aggregated_sig = aggregate_signatures(signatures)  # O(n) aggregation
    valid = aggregate_verify(messages, aggregated_sig, public_keys)  # O(1) verification

# RSA: Individual verification
elif scheme == "RSA":
    valid = aggregate_verify(messages, signatures, public_keys)  # O(n) verification

# EdDSA: Concatenation with individual verification
elif scheme == "EdDSA":
    aggregated_sig = aggregate_signatures(signatures)  # Concatenation
    valid = aggregate_verify(messages, aggregated_sig, public_keys)  # O(n) verification
```

## Performance Analysis

### Scalability Comparison

**Verification Time vs Number of Clients**:

```
Clients | BLS (O(1)) | RSA (O(n)) | EdDSA (O(n))
--------|------------|-----------|-------------
10      | 10ms       | 50ms      | 5ms
50      | 10ms       | 250ms     | 25ms
100     | 10ms       | 500ms     | 50ms
500     | 10ms       | 2500ms    | 250ms
```

**Key Insight**: BLS maintains constant verification time, while RSA and EdDSA scale linearly.

### Communication Overhead

**Total Signature Size**:

```
Clients | BLS (Aggregate) | RSA (Individual) | EdDSA (Individual)
--------|-----------------|------------------|-------------------
10      | 96 bytes        | 2560 bytes       | 640 bytes
50      | 96 bytes        | 12800 bytes      | 3200 bytes
100     | 96 bytes        | 25600 bytes      | 6400 bytes
500     | 96 bytes        | 128000 bytes     | 32000 bytes
```

**Key Insight**: BLS provides massive communication savings for large-scale FL.

## Conclusion

Non-homomorphic schemes (RSA, EdDSA) serve important roles:

1. **Baseline Comparison**: Demonstrate the benefits of homomorphic properties
2. **Practical Alternatives**: Suitable for small-scale FL scenarios
3. **Compliance**: Meet regulatory requirements for standard signatures
4. **Performance**: May be faster for small numbers of clients

However, for **large-scale Federated Learning**, homomorphic schemes (BLS) are clearly superior due to:
- Constant-time verification (O(1))
- Compact aggregate signatures
- Efficient communication

The inclusion of non-homomorphic schemes provides a **complete picture** of the trade-offs in authentication for FL systems.

