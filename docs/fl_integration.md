# Homomorphic Authentication in Federated Learning

## Overview

This document explains how homomorphic authentication mechanisms integrate into Federated Learning (FL) pipelines, covering both local model updates and global model aggregation.

## FL Pipeline Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Client 1  │         │   Client 2  │         │   Client N  │
│             │         │             │         │             │
│ Local Data  │         │ Local Data  │         │ Local Data  │
│     ↓       │         │     ↓       │         │     ↓       │
│ Local Train │         │ Local Train │         │ Local Train │
│     ↓       │         │     ↓       │         │     ↓       │
│ Local Update│         │ Local Update│         │ Local Update│
│     ↓       │         │     ↓       │         │     ↓       │
│ Authenticate│         │ Authenticate│         │ Authenticate│
│     ↓       │         │     ↓       │         │     ↓       │
│ [Optional]  │         │ [Optional]  │         │ [Optional]  │
│  Encrypt    │         │  Encrypt    │         │  Encrypt    │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       └───────────────────────┼───────────────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ FL Server     │
                        │               │
                        │ Receive       │
                        │ Updates       │
                        │     ↓         │
                        │ Aggregate     │
                        │ (Homomorphic) │
                        │     ↓         │
                        │ Verify        │
                        │ Aggregated    │
                        │ Auth          │
                        │     ↓         │
                        │ [Optional]    │
                        │ Decrypt       │
                        │     ↓         │
                        │ Update Global │
                        │ Model         │
                        └───────┬───────┘
                                │
                                ▼
                        ┌──────────────┐
                        │ Global Model │
                        └──────────────┘
```

## Client-Side Authentication of Local Updates

### Process Flow

1. **Local Update Computation**
   ```python
   # Client computes local model update
   local_update = train_local_model(local_data, global_model)
   ```

2. **Authentication**
   ```python
   # Sign or generate MAC tag
   if using_signature:
       signature = sign(local_update, private_key)
   else:
       tag = generate_mac(local_update, secret_key, client_id)
   ```

3. **Optional Encryption**
   ```python
   # Encrypt update using homomorphic encryption
   if use_he:
       encrypted_update = encrypt(local_update, public_key_he)
   ```

4. **Send to Server**
   ```python
   message = {
       "update": encrypted_update or local_update,
       "auth_tag": signature or tag,
       "metadata": {...}
   }
   send_to_server(message)
   ```

### Authentication Schemes

#### Digital Signatures (Public Key)
- **BLS**: Client signs update with private key, server verifies with public key
- **LHS**: Client signs vector update, supports linear combination verification
- **RSA/EdDSA**: Standard signature schemes with aggregation support

#### Homomorphic MAC (Symmetric Key)
- **Additive HMAC**: Client generates tag with shared secret
- **Linear HMAC**: Client generates tag for vector update
- Server can combine tags homomorphically

### Integration with Homomorphic Encryption

When both authentication and encryption are used:

```
Local Update
    ↓
[Authenticate] → Signature/Tag
    ↓
[Encrypt] → Encrypted Update
    ↓
Send: {encrypted_update, signature/tag}
```

**Important Considerations:**
- Authentication can be applied before or after encryption
- **Before encryption**: Sign plaintext update (more secure, verifies actual update)
- **After encryption**: Sign ciphertext (verifies encrypted form, but can't verify plaintext)

**Recommended Approach:**
- Sign plaintext update first
- Then encrypt the update
- Send both encrypted update and signature
- Server decrypts, then verifies signature on plaintext

## Server-Side Verification of Aggregated/Global Models

### Aggregation Process

1. **Receive Updates**
   ```python
   client_updates = [receive_from_client(i) for i in clients]
   ```

2. **Homomorphic Aggregation of Updates**
   ```python
   # If encrypted:
   aggregated_encrypted = aggregate_encrypted(encrypted_updates)
   
   # If plaintext:
   aggregated_update = fedavg(updates)  # Federated averaging
   ```

3. **Homomorphic Aggregation of Authentication**
   ```python
   # Aggregate signatures/tags
   if using_BLS:
       aggregated_sig = aggregate_signatures(signatures)
   elif using_additive_HMAC:
       aggregated_tag = combine_tags(tags)
   elif using_linear_HMAC:
       aggregated_tag = linear_combine_tags(tags, coefficients)
   ```

4. **Verification**
   ```python
   # Verify aggregated authentication
   if using_aggregate_verify:
       valid = aggregate_verify(
           aggregated_update,
           aggregated_sig,
           messages,
           public_keys
       )
   else:
       # Verify individual signatures
       valid = all(verify(update, sig, pk) 
                  for update, sig, pk in zip(updates, sigs, pks))
   ```

### How Homomorphism Helps in FL Context

### The FL Challenge

**Traditional FL Aggregation:**
- FL server needs to aggregate updates from many clients: `w_global = (1/n) · Σ w_i`
- Without homomorphic authentication: Must verify each client's update individually
- Cost: O(n) verification operations for n clients

### How Homomorphism Solves This

**Homomorphic Authentication Enables:**
1. **Aggregate First, Verify Once**: Instead of verifying n individual signatures, aggregate them into one signature and verify once
2. **Efficiency**: O(1) verification instead of O(n)
3. **Compatibility**: Homomorphic operations align with FL's additive aggregation

**Example:**
```
Without Homomorphism:
  Verify(sig₁) AND Verify(sig₂) AND ... AND Verify(sigₙ)  → n operations

With Homomorphism (BLS):
  Aggregate(sig₁, sig₂, ..., sigₙ) → sig_agg
  Verify(sig_agg, {pk₁, pk₂, ..., pkₙ})  → 1 operation
```

### Homomorphic Properties in Aggregation

#### For Digital Signatures:

**BLS Aggregation:**
```
σ_agg = σ1 · σ2 · ... · σn
Verify: e(σ_agg, g) = ∏ e(H(m_i), pk_i)
```
- **Benefit**: n signatures → 1 signature (96 bytes total)
- **Verification**: Single pairing operation instead of n

**LHS Linear Combination:**
```
v_agg = Σ α_i · v_i
σ_agg = Combine(σ1, σ2, ..., α1, α2, ...)
Verify: Verify(pk, v_agg, σ_agg)
```
- **Benefit**: Verify linear combination directly
- **Use Case**: Perfect for FedAvg with different client weights

#### For Homomorphic MAC:

**Additive Combination:**
```
tag_agg = tag1 + tag2 + ... + tag_n
m_agg = m1 + m2 + ... + m_n
Verify: tag_agg = MAC(k, m_agg)
```
- **Benefit**: Fast symmetric operations
- **Use Case**: Trusted server scenarios

**Linear Combination:**
```
tag_agg = Σ α_i · tag_i
v_agg = Σ α_i · v_i
Verify: tag_agg = MAC(k, v_agg)
```
- **Benefit**: Supports weighted aggregation
- **Use Case**: FedAvg with different client contributions

### Why This Matters for FL

1. **Scalability**: As number of clients grows, homomorphic verification stays constant (O(1))
2. **Communication**: Aggregate signatures are compact (BLS: 96 bytes for any number of clients)
3. **Compatibility**: Homomorphic operations match FL's additive aggregation naturally
4. **Efficiency**: Single verification instead of many individual verifications

## Interaction with Homomorphic Encryption

### Combined Protocol

```
┌─────────────────────────────────────────────────────────┐
│ Client Side                                             │
├─────────────────────────────────────────────────────────┤
│ 1. Compute local update: Δw_i                           │
│ 2. Authenticate: σ_i = Sign(Δw_i, sk_i)                │
│ 3. Encrypt: c_i = Encrypt(Δw_i, pk_HE)                 │
│ 4. Send: (c_i, σ_i)                                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Server Side                                             │
├─────────────────────────────────────────────────────────┤
│ 1. Receive: {(c_i, σ_i)} for all clients               │
│ 2. Aggregate encrypted: c_agg = Σ c_i                  │
│ 3. Aggregate signatures: σ_agg = Aggregate(σ_i)        │
│ 4. Decrypt: Δw_agg = Decrypt(c_agg, sk_HE)              │
│ 5. Verify: Verify(Δw_agg, σ_agg, {pk_i})                │
│ 6. Update: w_global = w_global + Δw_agg                 │
└─────────────────────────────────────────────────────────┘
```

### Security Properties

**Confidentiality:**
- Homomorphic encryption ensures updates remain private
- Server can aggregate without seeing plaintext

**Integrity:**
- Homomorphic authentication ensures updates are authentic
- Aggregated result can be verified

**Verifiability:**
- Public key schemes: Anyone can verify
- MAC schemes: Server (with secret key) can verify

## Local vs Global Models

### Local Model Updates

**What is authenticated:**
- Individual client's local model update/gradient
- Computed from client's local dataset

**Authentication purpose:**
- Prevent malicious clients from sending incorrect updates
- Ensure updates come from legitimate clients
- Detect tampering during transmission

**Example:**
```python
# Client i
local_update = compute_gradient(local_data, global_model)
signature = sign(local_update, client_i_private_key)
send_to_server(local_update, signature)
```

### Global Model Aggregation

**What is verified:**
- Aggregated update from all clients
- Result of homomorphic aggregation

**Verification purpose:**
- Verify aggregation was performed correctly
- Ensure no updates were tampered with
- Detect if aggregation is valid

**Example:**
```python
# Server
updates = [receive_from_client(i) for i in range(n)]
aggregated_update = fedavg(updates)
aggregated_sig = aggregate_signatures(signatures)
valid = aggregate_verify(aggregated_update, aggregated_sig, ...)
```

## Threat Models

### Malicious Clients

**Threat:**
- Clients send incorrect or adversarial updates
- Clients try to poison the global model

**Mitigation:**
- Authentication ensures updates are from registered clients
- Verification detects invalid updates
- Aggregation with verification ensures only valid updates contribute

### Malicious Server

**Threat:**
- Server modifies updates before aggregation
- Server claims incorrect aggregation result

**Mitigation:**
- Public verifiability (with signatures) allows auditing
- Homomorphic aggregation enables verification without revealing individual updates
- Clients can verify aggregated result matches their contributions

### Honest-but-Curious Server

**Threat:**
- Server tries to infer client data from updates

**Mitigation:**
- Homomorphic encryption hides individual updates
- Server only sees encrypted updates and aggregated result

## Performance Considerations

### Communication Overhead

**Per Client:**
- Update size: `d * sizeof(float)` where `d` is model dimension
- Authentication: Signature/tag size (32-256 bytes)
- Total: Update + Auth overhead

**After Aggregation:**
- Aggregate signature: Single signature (BLS) or combined tag
- Compression ratio: `n signatures → 1 signature` (for BLS)

### Computational Overhead

**Client Side:**
- Signing/MAC generation: O(1) per update
- Encryption: O(d) where d is dimension

**Server Side:**
- Aggregation: O(n*d) for n clients
- Signature aggregation: O(n) for BLS, O(1) for MAC
- Verification: O(1) for aggregate verify, O(n) for individual

## Concrete FL Scenario: Detailed Analysis

### Scenario Definition

**Setup:**
- 100 clients participating in FL
- Model dimension: 1000 (vector of 1000 floats)
- FL rounds: 10
- Authentication: BLS signatures
- Encryption: Homomorphic Encryption (CKKS scheme)

### What is Signed/MAC'ed

**For Digital Signatures (BLS, LHS, etc.):**
- **Raw update bytes**: The model update (numpy array) is converted to bytes using `.tobytes()`
- **Not hashed**: We sign the raw update bytes directly
- **Not encrypted first**: Authentication is applied to plaintext, then encryption is applied

**For Homomorphic MACs:**
- **Raw update bytes**: Same as signatures
- **With identifier**: Client ID is used as identifier for tag generation

**Code Example:**
```python
# Client-side
model_update = compute_local_gradient()  # numpy array
update_bytes = model_update.tobytes()  # Convert to bytes
signature = bls.sign(update_bytes)  # Sign raw bytes
encrypted_update = he.encrypt(model_update)  # Encrypt after signing
```

### How It Supports Global Model Verification/Aggregation

**Process:**
1. **Client sends**: `(encrypted_update, signature, public_key)`
2. **Server receives**: All client updates
3. **Server aggregates encrypted updates**: `encrypted_agg = Σ encrypted_updates` (homomorphic addition)
4. **Server aggregates signatures**: `sig_agg = Aggregate(sig₁, sig₂, ..., sigₙ)` (BLS aggregation)
5. **Server decrypts**: `plaintext_agg = Decrypt(encrypted_agg)`
6. **Server verifies**: `Verify(plaintext_agg, sig_agg, {pk₁, pk₂, ..., pkₙ})` (single aggregate verification)

**Homomorphic Properties:**
- BLS: `Aggregate(sig₁, sig₂) = sig₁ · sig₂` (group multiplication)
- HMAC: `Combine(tag₁, tag₂) = tag₁ + tag₂` (additive)
- Verification: Single verification of aggregated result instead of n individual verifications

### Communication Cost Per FL Round

**Per Client (100 clients):**
- Update size: 1000 floats × 4 bytes = 4,000 bytes
- Signature size: 96 bytes (BLS)
- Public key size: 48 bytes (sent once, not per round)
- Metadata: 16 bytes (nonce) + 32 bytes (commitment) = 48 bytes
- **Total per client per round**: 4,000 + 96 + 48 = 4,144 bytes ≈ 4.04 KB

**Server Aggregation:**
- Aggregated signature: 96 bytes (same size as single signature)
- **Compression ratio**: 100 signatures → 1 signature (96:1 compression)

**Total per Round:**
- From clients: 100 × 4,144 = 414,400 bytes ≈ 404 KB
- To clients: Global model (4,000 bytes) + aggregated signature (96 bytes) = 4,096 bytes ≈ 4 KB
- **Total communication**: ~408 KB per round

### Computation Overhead Per Participant

**Client-Side (per round):**
- Local training: ~100ms (simulated)
- Signing: ~2ms (BLS signing)
- Encryption: ~50ms (HE encryption)
- **Total client overhead**: ~152ms per round

**Server-Side (per round):**
- Receiving updates: ~10ms
- Aggregating encrypted updates: ~200ms (homomorphic addition)
- Aggregating signatures: ~5ms (BLS aggregation)
- Decryption: ~100ms (HE decryption)
- Verification: ~10ms (aggregate verification)
- **Total server overhead**: ~325ms per round

**Comparison:**
- Without homomorphic properties: Server would need to verify 100 signatures individually (~1000ms)
- With homomorphic properties: Single aggregate verification (~10ms)
- **Speedup**: ~100x for verification

## Recommendations

### Scenario 1: Many Clients, Low Bandwidth
- **Use**: BLS aggregate signatures
- **Reason**: Compact aggregate signature, single verification

### Scenario 2: Trusted Server, High Performance
- **Use**: Additive/Linear HMAC
- **Reason**: Fast symmetric operations, low overhead

### Scenario 3: Public Verifiability Required
- **Use**: BLS or LHS signatures
- **Reason**: Public key verification, auditability

### Scenario 4: Privacy + Integrity
- **Use**: HE + Homomorphic Authentication
- **Reason**: Confidentiality from HE, integrity from authentication

### Scenario 5: High-Dimensional Updates
- **Use**: Linear HMAC or LHS
- **Reason**: Efficient vector operations

