# Code Implementation Details

## Homomorphic Encryption Library

### Library Used: Microsoft SEAL (via TenSEAL)

**TenSEAL (Python Wrapper):**
- **GitHub**: https://github.com/OpenMined/TenSEAL
- **License**: Apache 2.0
- **Documentation**: https://github.com/OpenMined/TenSEAL

**Microsoft SEAL (C++ Library):**
- **GitHub**: https://github.com/microsoft/SEAL
- **License**: MIT
- **Documentation**: https://www.microsoft.com/en-us/research/project/microsoft-seal/

**Installation:**
```bash
pip install tenseal
```

**Usage in Code:**
```python
import tenseal as ts

# Create CKKS context
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)

# Generate keys
context.generate_galois_keys()
context.global_scale = 2**40

# Encrypt vector
encrypted = ts.ckks_vector(context, data.tolist())

# Homomorphic operations
result = encrypted1 + encrypted2  # Addition
```

**Verification:**
The code checks if `tenseal` is available and uses it. If not available, a fallback is used (with warning).

## Algorithm References

### Open-Source Implementations

1. **BLS Signatures**
   - **Library**: blspy
   - **GitHub**: https://github.com/Chia-Network/blspy
   - **License**: Apache 2.0
   - **Status**: ✅ Fully open-source

### Research-Based Implementations

2. **Linearly Homomorphic Signatures (LHS)**
   - **Reference**: Catalano-Fiore construction
   - **Paper**: "Linearly Homomorphic Signatures over Binary Fields and New Tools for Lattice-Based Signatures"
   - **Link**: https://eprint.iacr.org/2011/035
   - **Status**: Custom implementation based on published construction

3. **Waters Homomorphic Signature**
   - **Reference**: Waters signature scheme
   - **Paper**: "Efficient Identity-Based Encryption Without Random Oracles"
   - **Link**: https://www.iacr.org/archive/eurocrypt2005/34940001/34940001.pdf
   - **Status**: Custom implementation based on published scheme

4. **Boneh-Boyen Homomorphic Signature**
   - **Reference**: Boneh-Boyen signature scheme
   - **Paper**: "Short Signatures Without Random Oracles"
   - **Link**: https://www.iacr.org/archive/eurocrypt2004/30270001/30270001.pdf
   - **Status**: Custom implementation based on published scheme

5. **Homomorphic MACs**
   - **Reference**: "Homomorphic Message Authenticators" by Catalano and Fiore
   - **Paper**: https://eprint.iacr.org/2014/415
   - **Status**: Custom implementations based on published constructions

## Why Custom Implementations?

**Reason**: Most homomorphic authentication schemes are research-level and don't have complete, production-ready open-source implementations. The implementations in this project are based on:
1. Published academic papers with detailed constructions
2. Standard cryptographic primitives (hash functions, group operations)
3. Well-documented security properties

**Justification**: For applied research and benchmarking purposes, implementations based on published constructions are acceptable when:
- The construction is clearly documented in peer-reviewed papers
- The implementation follows the published algorithms
- Security properties are maintained
- The purpose is comparative analysis, not production deployment

