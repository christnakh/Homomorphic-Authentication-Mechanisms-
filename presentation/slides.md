# Homomorphic Authentication in Federated Learning
## Comparative Analysis and Benchmarking

---

## Slide 1: Title Slide

**Homomorphic Authentication in Federated Learning**

A Comprehensive Benchmarking and Comparative Analysis

- 4 Homomorphic Digital Signature Schemes
- 4 Homomorphic MAC Schemes
- FL Integration Analysis
- Performance-Security Trade-offs

---

## Slide 2: Context and Problem Formulation

### Federated Learning Challenges

**Security Requirements:**
1. **Integrity**: Authenticate model updates
2. **Privacy**: Protect client data
3. **Verifiability**: Verify aggregation correctness

### Problem Statement

**Traditional Approach:**
- Verify each client's update individually
- O(n) verification cost for n clients
- High communication overhead

**Homomorphic Authentication Solution:**
- Aggregate n signatures/tags into one
- O(1) verification of aggregated result
- Reduced communication overhead

---

## Slide 3: Motivation

### Why Homomorphic Authentication?

**Scalability:**
```
Traditional: Verify(σ₁) ∧ Verify(σ₂) ∧ ... ∧ Verify(σₙ)  → O(n)
Homomorphic: Verify(Aggregate(σ₁, σ₂, ..., σₙ))          → O(1)
```

**Efficiency:**
- Single aggregate verification instead of n individual
- Compact aggregate signatures (e.g., BLS: 96 bytes for n clients)

**Compatibility:**
- Homomorphic properties align with FL's additive aggregation
- Natural integration with homomorphic encryption

---

## Slide 4: Contribution

### What This Project Provides

1. **Comprehensive Benchmarking**
   - 8 homomorphic authentication schemes
   - Performance metrics (time, memory, communication)
   - Scalability analysis

2. **FL Integration Analysis**
   - Client-side authentication
   - Server-side verification
   - HE integration

3. **Comparative Evaluation**
   - Security-performance trade-offs
   - Algorithm selection guidelines

4. **Open Implementation**
   - Reproducible benchmarking framework
   - FL simulation with authentication

---

## Slide 5: Selected Algorithms

### Homomorphic Digital Signatures

1. **BLS Aggregate Signatures**
   - Library: blspy (Chia Network)
   - Compact aggregation, public verifiability

2. **Linearly Homomorphic Signatures (LHS)**
   - Custom implementation
   - Linear combination verification

3. **RSA-based Homomorphic**
   - Library: pycryptodome
   - Multiplicative homomorphism

4. **EdDSA with Aggregation**
   - Library: cryptography
   - Fast signing, aggregation support

### Homomorphic MAC/HMA

1. **Additive HMAC** - Additive tag combination
2. **Linear HMAC** - Linear combination
3. **Polynomial HMAC** - Polynomial operations
4. **Lattice HMAC** - Lattice-based (post-quantum)

---

## Slide 6: Algorithm Overview - BLS

### BLS Aggregate Signatures

**How It Works:**
```
KeyGen:  sk ∈ Z_q, pk = g^sk
Sign:    σ = H(m)^sk
Verify:  e(σ, g) = e(H(m), pk)
Aggregate: σ_agg = σ₁ · σ₂ · ... · σₙ
AggVerify: e(σ_agg, g) = ∏ e(H(m_i), pk_i)
```

**Properties:**
- ✓ Compact aggregate (96 bytes)
- ✓ Public verifiability
- ✓ Efficient aggregation
- ✗ Pairing operations (expensive)

**Open Source:** https://github.com/Chia-Network/blspy

---

## Slide 7: Algorithm Overview - Homomorphic MACs

### Additive/Linear HMAC

**How It Works:**
```
KeyGen:  k (shared secret)
TagGen:  tag = MAC(k, id, m)
Verify:  tag == MAC(k, id, m)
Combine: tag_agg = tag₁ + tag₂ + ... + tagₙ  (additive)
         tag_agg = Σ αᵢ · tagᵢ                (linear)
```

**Properties:**
- ✓ Very fast (symmetric crypto)
- ✓ Small tags (32 bytes)
- ✓ Efficient aggregation
- ✗ No public verifiability
- ✗ Requires secret key distribution

---

## Slide 8: FL Integration - Architecture

### System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Client 1   │     │  Client 2   │     │  Client N   │
│             │     │             │     │             │
│ Local Data  │     │ Local Data  │     │ Local Data  │
│     ↓       │     │     ↓       │     │     ↓       │
│ Local Train │     │ Local Train │     │ Local Train │
│     ↓       │     │     ↓       │     │     ↓       │
│ Local Update│     │ Local Update│     │ Local Update│
│     ↓       │     │     ↓       │     │     ↓       │
│ Authenticate│     │ Authenticate│     │ Authenticate│
│     ↓       │     │     ↓       │     │     ↓       │
│ [Encrypt]   │     │ [Encrypt]   │     │ [Encrypt]   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ FL Server     │
                    │               │
                    │ Aggregate     │
                    │ Verify        │
                    │ Update Global │
                    └───────────────┘
```

---

## Slide 9: FL Integration - Client Side

### Client-Side Authentication (Pseudo-code)

```python
# Client i prepares authenticated update
function prepare_update(global_model):
    # 1. Compute local update
    local_update = train_local_model(local_data, global_model)
    
    # 2. Authenticate update
    if using_signature:
        signature = sign(local_update, private_key_i)
        auth_tag = signature
        metadata = {public_key: public_key_i}
    else:  # using MAC
        tag = generate_mac(local_update, secret_key, client_id_i)
        auth_tag = tag
        metadata = {identifier: client_id_i}
    
    # 3. Optionally encrypt
    if use_he:
        encrypted_update = encrypt(local_update, he_public_key)
        update = encrypted_update
    else:
        update = local_update
    
    # 4. Send to server
    return {
        update: update,
        auth_tag: auth_tag,
        metadata: metadata
    }
```

**Key Points:**
- Authenticate before encryption (verify actual update)
- Include metadata (public keys, identifiers)
- Support both signatures and MACs

---

## Slide 10: FL Integration - Server Side

### Server-Side Aggregation and Verification (Pseudo-code)

```python
# Server aggregates and verifies
function aggregate_and_verify(client_updates):
    updates = []
    auth_tags = []
    public_keys = []
    
    # 1. Collect updates and authentication
    for update_data in client_updates:
        updates.append(update_data.update)
        auth_tags.append(update_data.auth_tag)
        if "public_key" in update_data.metadata:
            public_keys.append(update_data.metadata.public_key)
    
    # 2. Aggregate updates (homomorphically if encrypted)
    if encrypted:
        aggregated_update = aggregate_encrypted(updates)
    else:
        aggregated_update = fedavg(updates)  # Federated averaging
    
    # 3. Aggregate authentication tags/signatures
    if using_BLS:
        aggregated_sig = aggregate_signatures(auth_tags)
    elif using_additive_HMAC:
        aggregated_tag = combine_tags(auth_tags)
    elif using_linear_HMAC:
        aggregated_tag = linear_combine_tags(auth_tags, coefficients)
    
    # 4. Verify aggregated authentication
    if using_aggregate_verify:
        valid = aggregate_verify(
            aggregated_update,
            aggregated_sig,
            messages,
            public_keys
        )
    else:
        valid = verify_individual(auth_tags, updates, public_keys)
    
    # 5. Decrypt if needed
    if encrypted:
        aggregated_update = decrypt(aggregated_update, he_secret_key)
    
    # 6. Update global model
    global_model = global_model + learning_rate * aggregated_update
    
    return {valid: valid, global_model: global_model}
```

---

## Slide 11: Homomorphic Properties

### How Homomorphism Helps in FL

**Additive Aggregation in FL:**
```
Global Update = (1/n) · Σ Local_Update_i
```

**Homomorphic Authentication:**
```
For Signatures (BLS):
  Aggregate(Sign(Δw₁), Sign(Δw₂), ..., Sign(Δwₙ))
  = Sign(Δw₁ + Δw₂ + ... + Δwₙ)  [conceptually]

For MACs (Additive):
  Combine(MAC(Δw₁), MAC(Δw₂), ..., MAC(Δwₙ))
  = MAC(Δw₁ + Δw₂ + ... + Δwₙ)
```

**Benefits:**
- Verify aggregated result directly
- No need to verify individual updates
- Efficient for many clients

---

## Slide 12: Integration with Homomorphic Encryption

### Combined Protocol (Block Diagram)

```
┌─────────────────────────────────────────────────────────┐
│ Client Side                                             │
├─────────────────────────────────────────────────────────┤
│ 1. Compute: Δw_i = local_gradient()                     │
│ 2. Authenticate: σ_i = Sign(Δw_i, sk_i)                │
│ 3. Encrypt: c_i = Encrypt(Δw_i, pk_HE)                 │
│ 4. Send: (c_i, σ_i)                                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Server Side                                             │
├─────────────────────────────────────────────────────────┤
│ 1. Receive: {(c_i, σ_i)} for i = 1..n                  │
│ 2. Aggregate encrypted: c_agg = Σ c_i                  │
│ 3. Aggregate signatures: σ_agg = Aggregate(σ_i)        │
│ 4. Decrypt: Δw_agg = Decrypt(c_agg, sk_HE)              │
│ 5. Verify: Verify(Δw_agg, σ_agg, {pk_i})               │
│ 6. Update: w_global = w_global + Δw_agg                 │
└─────────────────────────────────────────────────────────┘
```

**Security Properties:**
- **Confidentiality**: HE protects individual updates
- **Integrity**: Authentication ensures authenticity
- **Verifiability**: Aggregated result can be verified

---

## Slide 13: Benchmarking Methodology

### Experimental Setup

**Metrics Collected:**
- Execution time (key gen, signing, verification, aggregation)
- Memory usage (peak, average)
- Communication overhead (signature/tag sizes)
- Scalability (performance vs number of clients)

**Parameter Ranges:**
- Clients: 10, 50, 100, 500
- Message sizes: 1KB, 4KB, 16KB, 64KB
- Vector dimensions: 100, 1000, 10000
- FL rounds: 1, 5, 10

**Benchmark Framework:**
- Automated metric collection
- Reproducible experiments
- Visualization tools

---

## Slide 14: Benchmark Results - Performance

### Performance Comparison

**Key Generation Time:**
- BLS: 0.01ms
- LHS/Waters/BonehBoyen: 0.002-0.003ms
- RSA: 666ms (slowest)
- EdDSA: 2.4ms
- HMACs: <0.001ms (fastest)

**Signing Time (1KB messages):**
- BLS: 0.002ms
- LHS: 0.004ms
- Waters/BonehBoyen: 0.002ms
- RSA: 2.765ms (slowest)
- EdDSA: 0.225ms
- HMACs: 0.003-0.030ms

**Aggregation Time (20 clients):**
- BLS: 0.075ms
- Other homomorphic: ~0.04ms
- HMACs: ~0.04ms

**Key Findings:**
- **BLS**: Fast aggregation, efficient for many clients
- **HMACs**: Very fast (symmetric crypto)
- **LHS/Waters/BonehBoyen**: Fast and efficient
- **RSA**: Slowest (large key sizes, no aggregation)

**Scalability:**
- Aggregate verification: O(1) for homomorphic schemes
- Individual verification: O(n) for RSA/EdDSA
- Aggregation time: Linear with number of clients (O(n))

---

## Slide 15: Benchmark Results - Communication

### Communication Overhead

**Signature/Tag Sizes (per client):**
- BLS: 96 bytes
- LHS/Waters/BonehBoyen: 32 bytes
- EdDSA: 64 bytes
- RSA: 256 bytes
- HMACs: 32 bytes

**After Aggregation:**
- BLS: 96 bytes (n → 1 compression)
- LHS/Waters/BonehBoyen: 32 bytes (n → 1)
- HMACs: 32 bytes (n → 1)
- RSA: 256n bytes (no compression)
- EdDSA: 64n bytes (no compression)

**Compression Ratio:**
- BLS: n → 1 (best compression, largest base size)
- LHS/Waters/BonehBoyen: n → 1 (best compression, smallest base size)
- HMACs: n → 1 (additive combination)
- RSA/EdDSA: n → n (no compression)

**Key Sizes:**
- BLS: 48 bytes (public key)
- LHS/Waters/BonehBoyen: 32 bytes
- EdDSA: 32 bytes
- RSA: 256 bytes
- HMACs: 32 bytes (secret key, shared)

**Total Communication (100 clients, 1KB updates):**
- BLS: ~105KB (includes keys + aggregate)
- RSA: ~150KB (no compression)
- HMACs: ~100KB (smallest, but requires secret key)

---

## Slide 16: Security Analysis

### Security Properties Comparison

| Scheme | Security Notion | Public Verify | Aggregation | Homomorphic Op |
|--------|----------------|---------------|-------------|----------------|
| BLS | EUF-CMA | ✓ | ✓ | Multiplicative |
| LHS | EUF-CMA | ✓ | ✓ | Linear |
| RSA | EUF-CMA | ✓ | Limited | Multiplicative |
| EdDSA | EUF-CMA | ✓ | Protocol | Limited |
| Additive HMAC | Unforgeability | ✗ | ✓ | Addition |
| Linear HMAC | Unforgeability | ✗ | ✓ | Linear |
| Polynomial HMAC | Unforgeability | ✗ | ✓ | Polynomial |
| Lattice HMAC | LWE-based | ✗ | ✓ | Various |

**Adversarial Models:**
- Malicious clients: All schemes resistant
- Malicious server: Only public-key schemes provide protection
- Honest-but-curious: HE needed for privacy

---

## Slide 17: Security-Performance Trade-offs

### Trade-off Analysis

[Insert security-performance trade-off chart]

**Key Trade-offs:**

1. **Public Verifiability vs Performance**
   - Signatures: Public verifiable but slower
   - MACs: Fast but require secret key

2. **Aggregation Efficiency**
   - BLS: O(1) aggregate verification
   - MACs: O(1) tag combination
   - Individual: O(n) verification

3. **Communication vs Computation**
   - BLS: Compact but expensive pairing
   - HMACs: Small tags, fast computation
   - RSA: Large signatures, moderate computation

---

## Slide 18: Recommendations

### Algorithm Selection Guide

| Scenario | Recommended Scheme | Reason |
|----------|-------------------|--------|
| Many clients, low bandwidth | **BLS** | Compact aggregate signature (n→1) |
| Trusted server, high performance | **Additive/Linear HMAC** | Fast symmetric operations |
| Public verifiability required | **BLS or LHS** | Public key verification |
| Privacy + Integrity | **HE + BLS/HMAC** | Both confidentiality and integrity |
| High-dimensional updates | **Linear HMAC or LHS** | Efficient vector operations |
| Post-quantum security | **Lattice HMAC** | Quantum-resistant (theoretical) |
| Low-latency FL | **Additive HMAC** | Fastest operations |
| High-throughput FL | **BLS** | Efficient aggregation |
| Untrusted aggregator | **BLS or LHS** | Public verifiability |
| Trusted aggregator | **Any HMAC** | Fastest, most efficient |
| Malicious clients | **All schemes** | All provide integrity |
| Malicious server | **BLS, LHS** | Public verifiability enables auditing |
| Honest-but-curious server | **HE + Any** | Encryption provides privacy |

### Integration Guidelines

**For Local Updates:**
- Authenticate before encryption (verify actual update)
- Use appropriate scheme based on threat model
- Consider communication overhead

**For Global Aggregation:**
- Leverage homomorphic properties for efficient verification
- Use aggregate verification when possible
- Verify aggregated result matches individual contributions

**Combining HE with Authentication to Achieve Both Privacy and Verifiability:**
1. **Client**: Sign plaintext update, then encrypt
2. **Server**: Aggregate encrypted updates (HE homomorphism)
3. **Server**: Aggregate signatures/tags (Auth homomorphism)
4. **Server**: Decrypt aggregated result
5. **Server**: Verify aggregated signature on plaintext

**Benefits:**
- ✅ Privacy: Server never sees individual plaintext updates
- ✅ Integrity: Can verify aggregated result is authentic
- ✅ Efficiency: Both operations are homomorphic
- ✅ Verifiability: Public-key schemes enable auditing

---

## Slide 19: Demo - Implementation Overview

### Benchmarking Framework

**Components:**
1. Algorithm implementations/wrappers
2. FL pipeline simulation
3. Metrics collection
4. Visualization tools

**Usage:**
```bash
# Run benchmarks
python experiments/run_benchmarks.py --config config/benchmark_config.yaml --plots

# Run FL simulation
python experiments/fl_simulation.py --clients 100 --rounds 10 --auth_scheme BLS
```

**Output:**
- Performance metrics (JSON, CSV)
- Communication analysis
- Security properties
- Visualization plots

---

## Slide 20: Demo - FL Simulation

### FL Simulation with Authentication

**Scenario:**
- 100 clients
- 10 FL rounds
- BLS authentication
- Homomorphic encryption

**Process:**
1. Clients compute local updates
2. Clients authenticate updates (BLS signatures)
3. Clients encrypt updates (HE)
4. Server aggregates encrypted updates
5. Server aggregates signatures
6. Server decrypts and verifies
7. Server updates global model

**Metrics:**
- Aggregation time per round
- Verification time per round
- Communication overhead
- Verification success rate

---

## Slide 21: Limitations and Future Work

### Current Limitations

- Simplified implementations for some schemes
- Limited to linear/additive operations
- Key distribution not fully addressed
- Post-quantum schemes need more development

### Future Work

- Implement full LHS construction
- Add more post-quantum schemes
- Study non-linear aggregation schemes
- Analyze key distribution protocols
- Real-world FL system integration
- Performance optimization

---

## Slide 22: Conclusion

### Key Takeaways

1. **Homomorphic authentication** enables efficient verification in FL
2. **BLS signatures** offer best balance for public verifiability
3. **Homomorphic MACs** provide superior performance for trusted environments
4. **Linear schemes** are ideal for FL's additive aggregation
5. **Combined HE + Authentication** enables both privacy and integrity

### Impact

- Provides guidance for FL system designers
- Enables secure and efficient FL deployments
- Demonstrates practical integration approaches
- Open-source benchmarking framework

---

## Slide 23: Questions & Discussion

### Thank You!

**Project Repository:**
- Code: [GitHub link]
- Documentation: `docs/`
- Results: `results/`

**Contact:**
- Questions welcome!

---

## Appendix: Pseudo-code Details

### BLS Aggregation (Detailed)

```python
# BLS Signature Aggregation
def aggregate_signatures_BLS(signatures):
    """
    Aggregate multiple BLS signatures into one
    
    Input: signatures = [σ₁, σ₂, ..., σₙ]
    Output: σ_agg = σ₁ · σ₂ · ... · σₙ
    """
    aggregated = G2Element()  # Identity element
    for sig in signatures:
        aggregated = aggregated * sig  # Group multiplication
    return aggregated

def aggregate_verify_BLS(messages, aggregated_sig, public_keys):
    """
    Verify aggregated BLS signature
    
    Input:
      messages: [m₁, m₂, ..., mₙ]
      aggregated_sig: σ_agg
      public_keys: [pk₁, pk₂, ..., pkₙ]
    
    Verification: e(σ_agg, g) = ∏ e(H(m_i), pk_i)
    """
    left = pairing(aggregated_sig, g)  # e(σ_agg, g)
    right = G1Element()  # Identity
    for msg, pk in zip(messages, public_keys):
        H_msg = hash_to_G2(msg)
        right = right * pairing(H_msg, pk)  # ∏ e(H(m_i), pk_i)
    return left == right
```

### Linear HMAC Combination (Detailed)

```python
# Linear HMAC Combination
def linear_combine_tags(tags, coefficients):
    """
    Linearly combine HMAC tags
    
    Input:
      tags: [tag₁, tag₂, ..., tagₙ]
      coefficients: [α₁, α₂, ..., αₙ]
    
    Output: tag_agg = Σ αᵢ · tagᵢ
    """
    tag_agg = np.zeros(32, dtype=np.uint8)
    for tag, coeff in zip(tags, coefficients):
        tag_array = np.frombuffer(tag, dtype=np.uint8)
        tag_agg = (tag_agg + coeff * tag_array) % 256
    return tag_agg.tobytes()

def verify_linear_combination(vectors, combined_vector, 
                              combined_tag, coefficients, 
                              identifiers, secret_key):
    """
    Verify linear combination of tagged vectors
    
    Verification: tag_agg = MAC(k, Σ αᵢ · vᵢ)
    """
    # Generate expected tag
    expected_tag = generate_mac(combined_vector, secret_key, identifiers)
    
    # Verify tag matches
    tag_valid = (combined_tag == expected_tag)
    
    # Verify vector is correct linear combination
    expected_vector = sum(coeff * vec for coeff, vec 
                         in zip(coefficients, vectors))
    vector_valid = np.allclose(combined_vector, expected_vector)
    
    return tag_valid and vector_valid
```

---

## Appendix: Block Diagrams

### Complete FL Pipeline with Authentication and Encryption

```
┌─────────────────────────────────────────────────────────────┐
│                    FL ROUND k                                │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Client 1    │  │  Client 2    │  │  Client N    │
├──────────────┤  ├──────────────┤  ├──────────────┤
│ w_global     │  │ w_global     │  │ w_global     │
│     ↓        │  │     ↓        │  │     ↓        │
│ Local Train  │  │ Local Train  │  │ Local Train  │
│     ↓        │  │     ↓        │  │     ↓        │
│ Δw₁          │  │ Δw₂          │  │ Δwₙ          │
│     ↓        │  │     ↓        │  │     ↓        │
│ Sign(Δw₁)    │  │ Sign(Δw₂)    │  │ Sign(Δwₙ)    │
│     ↓        │  │     ↓        │  │     ↓        │
│ Enc(Δw₁)     │  │ Enc(Δw₂)     │  │ Enc(Δwₙ)     │
│     ↓        │  │     ↓        │  │     ↓        │
│ (c₁, σ₁)     │  │ (c₂, σ₂)     │  │ (cₙ, σₙ)     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   FL Server          │
              ├──────────────────────┤
              │ 1. Receive (c_i, σ_i)│
              │ 2. c_agg = Σ c_i     │
              │ 3. σ_agg = Agg(σ_i)  │
              │ 4. Δw = Dec(c_agg)   │
              │ 5. Verify(Δw, σ_agg) │
              │ 6. w = w + Δw        │
              └──────────────────────┘
                         │
                         ▼
                   w_global (k+1)
```

---

## Appendix: Security Analysis

### Threat Model Analysis

**Malicious Clients:**
- Threat: Send incorrect/adversarial updates
- Mitigation: Authentication ensures updates from registered clients
- Schemes: All schemes provide protection

**Malicious Server:**
- Threat: Modify updates or aggregation result
- Mitigation: Public verifiability (signatures), auditability
- Schemes: Only public-key schemes (BLS, LHS, RSA, EdDSA)

**Honest-but-Curious Server:**
- Threat: Infer client data from updates
- Mitigation: Homomorphic encryption
- Schemes: All schemes compatible with HE

**Network Adversary:**
- Threat: Tamper with updates in transit
- Mitigation: Authentication detects tampering
- Schemes: All schemes provide protection

