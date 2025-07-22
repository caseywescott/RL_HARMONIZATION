# Test Suite for RL_HARMONIZATION

This directory contains all the test files for the RL_HARMONIZATION system.

## 🧪 **Test Files Overview**

### **Core System Tests**

#### **Basic Functionality Tests**

- `test_simple.py` - Basic functionality tests for reward system, environment, and Coconet wrapper
- `test_implementation.py` - Implementation validation tests
- `test_training_simple.py` - Simple training process tests
- `test_trained_model.py` - Tests for trained model functionality

#### **Coconet Integration Tests**

- `test_coconet_harmonization.py` - Coconet harmonization functionality tests
- `test_coconet_properly.py` - Proper Coconet integration tests
- `test_real_coconet_integration.py` - Real Coconet model integration tests
- `test_model_loading.py` - Model loading and initialization tests

#### **RL Model Tests**

- `test_rl_harmonization.py` - RL harmonization model tests
- `test_simple_contrary_motion_model.py` - Contrary motion model tests
- `simple_test_model.py` - Simple RL model tests

#### **Hybrid System Tests**

- `test_hybrid_system.py` - Complete hybrid system integration tests
- `test_hybrid_model.py` - Hybrid model functionality tests
- `simple_hybrid_test.py` - Simple hybrid system tests

#### **Debug and Development Tests**

- `debug_test.py` - Debugging utilities and tests
- `test_masking_debug.py` - Masking functionality debug tests
- `test_working_harmonization.py` - Working harmonization validation tests

## 🚀 **Running Tests**

### **Individual Test Files**

```bash
# Run a specific test
python3 tests/test_simple.py

# Run hybrid system test
python3 tests/test_hybrid_system.py

# Run Coconet integration test
python3 tests/test_real_coconet_integration.py
```

### **All Tests (if you have pytest)**

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v
```

## 📋 **Test Categories**

### **Unit Tests**

- **Reward System**: Tests for music theory reward calculations
- **Environment**: Tests for RL environment functionality
- **Model Loading**: Tests for model initialization and loading

### **Integration Tests**

- **Coconet Integration**: Tests for neural network harmonization
- **RL Integration**: Tests for reinforcement learning components
- **Hybrid System**: Tests for complete Coconet+RL pipeline

### **System Tests**

- **End-to-End**: Complete harmonization pipeline tests
- **Performance**: System performance and optimization tests
- **Debug**: Debugging and troubleshooting tests

## 🔧 **Test Dependencies**

### **Required Packages**

- `numpy` - Numerical computations
- `pretty_midi` - MIDI file handling
- `requests` - HTTP requests for server tests
- `subprocess` - Process management for server tests

### **Optional Packages**

- `pytest` - Test framework (for advanced testing)
- `pytest-cov` - Coverage reporting

## 📊 **Test Coverage**

The test suite covers:

- ✅ **Core Components**: Reward system, environment, models
- ✅ **Integration**: Coconet and RL model integration
- ✅ **System**: Complete harmonization pipeline
- ✅ **Edge Cases**: Error handling and boundary conditions
- ✅ **Performance**: System performance validation

## 🐛 **Debugging Tests**

### **Common Issues**

1. **Import Errors**: Make sure you're running from the project root
2. **Path Issues**: Tests use relative paths from the tests/ directory
3. **Server Dependencies**: Some tests require the Coconet server to be running

### **Debug Mode**

```bash
# Run with debug output
python3 tests/debug_test.py

# Run specific debug tests
python3 tests/test_masking_debug.py
```

## 📈 **Test Results**

Tests validate:

- **Functionality**: All system components work correctly
- **Integration**: Components work together properly
- **Performance**: System meets performance requirements
- **Reliability**: System handles errors gracefully

## 🔄 **Adding New Tests**

When adding new tests:

1. Place them in the `tests/` directory
2. Use descriptive names starting with `test_`
3. Include proper import path fixes for the tests/ subdirectory
4. Add documentation in this README

---

**Total Test Files**: 18  
**Coverage**: Core system, integration, and end-to-end testing  
**Status**: ✅ All tests organized and import paths fixed
