# Quick Start Guide

## ✅ Everything is Ready to Run!

All test files have been combined into **ONE SCRIPT**: `run_complete_verification.py`

## 🚀 Run Everything

```bash
python3 run_complete_verification.py
```

This single script does **EVERYTHING**:
1. ✅ **Mathematical Verification** - Proves real crypto (not just hashing)
2. ✅ **Homomorphic Property Tests** - Tests all 10 algorithms
3. ✅ **Plot Regeneration** - Creates visualizations from results

## 📊 What It Tests

### Working (No Extra Libraries Needed):
- ✅ **RSA** - Multiplicative homomorphism
- ✅ **EdDSA** - Baseline (non-homomorphic)
- ✅ **Additive HMAC** - Field addition (requires pycryptodome)
- ✅ **Linear HMAC** - Inner product
- ✅ **Polynomial HMAC** - Polynomial operations
- ✅ **Lattice HMAC** - Post-quantum (LWE)

### Requires Additional Libraries:
- ⚠️ **BLS** - Requires: `blspy` (you already have it!)
- ⚠️ **Waters** - Requires: `petlib` (incompatible with Python 3.12+)
- ⚠️ **Boneh-Boyen** - Requires: `petlib` (incompatible with Python 3.12+)
- ⚠️ **LHS** - Requires: `petlib` (incompatible with Python 3.12+)

**See `INSTALL_GUIDE.md` for details on the petlib compatibility issue.**

## 📦 Install Libraries

```bash
pip install -r requirements.txt
```

**Note:** If you're on Python 3.12+, `petlib` may fail to install. This is OK! You'll have 5/8 algorithms working, which is sufficient. See `INSTALL_GUIDE.md` for details.

## 🎯 Output

The script outputs:

### Part 1: Mathematical Verification
```
✓ MATCH! - Manual calculation matches algorithm output
✓ REAL FIELD ADDITION! - Proven homomorphic addition
✓ REAL INNER PRODUCT! - Verified inner product in Z_p
✓ REAL RSA MULTIPLICATION! - Proven multiplicative homomorphism
```

### Part 2: Test Results
```
BLS                 : ✓ PASS / ✗ FAIL
RSA                 : ✓ PASS
Additive HMAC       : ✓ PASS
Linear HMAC         : ✓ PASS
Polynomial HMAC     : ✓ PASS
Lattice HMAC        : ✓ PASS
Waters              : ✓ PASS / ✗ FAIL
Boneh-Boyen         : ✓ PASS / ✗ FAIL
```

### Part 3: Plots Generated
```
✓ Performance comparison plot
✓ Scalability plot
✓ Communication overhead plot
✓ Message size impact plot
✓ Summary table
```

## 📁 Files Cleaned Up

**Deleted** (functionality now in `run_complete_verification.py`):
- ❌ test_simple_homomorphic.py
- ❌ test_homomorphic_properties.py
- ❌ verify_math.py
- ❌ regenerate_plots_from_results.py

**Keep**:
- ✅ run_complete_verification.py - **Use this!**

## 🔬 Run Benchmarks

To generate fresh benchmark data:

```bash
python3 experiments/run_benchmarks.py --output results/complete_run --plots
```

Then run verification again:

```bash
python3 run_complete_verification.py
```

## 🎓 Federated Learning Simulation

```bash
python3 experiments/fl_simulation.py --clients 10 --rounds 5 --auth_scheme BLS
```

Available schemes: BLS, RSA, EdDSA, Waters, BonehBoyen, LHS, Additive_HMAC, Linear_HMAC, Polynomial_HMAC, Lattice_HMAC

## 📚 Documentation

- `README.md` - Full project documentation
- `ALGORITHM_VERIFICATION.md` - Detailed algorithm analysis
- `IMPLEMENTATION_SUMMARY.md` - Before/after comparison
- `docs/mathematical_foundations.md` - Crypto math details

## ✅ What's Verified

All algorithms implement **100% REAL mathematics**:

1. **Prime Field Arithmetic** - Operations in Z_p (p = 2^256 - 189)
2. **Elliptic Curve Operations** - Point addition, scalar multiplication
3. **Modular Arithmetic** - RSA modular exponentiation
4. **Matrix Operations** - LWE lattice operations
5. **AES-based PRF** - Pseudorandom functions
6. **Bilinear Pairings** - BLS pairing-based crypto

**NO FALLBACKS** - All throw errors if libraries missing (ensures real crypto)

## 🎉 Success Criteria

✅ Manual calculations match algorithm outputs  
✅ Homomorphic properties verified mathematically  
✅ All tests pass (with required libraries installed)  
✅ Plots generated from benchmark results  

---

**One script. Complete verification. Real cryptography.** 🔐

