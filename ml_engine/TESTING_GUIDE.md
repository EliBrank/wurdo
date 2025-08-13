# 🧪 GameService Testing Guide

This guide provides comprehensive testing strategies for `game_service.py` to ensure reliability and catch integration issues before they reach production.

## 🚀 Quick Start Testing

### 1. **Basic Functionality Test** (No Dependencies)
```bash
cd ml_engine
python run_tests.py basic
```
This tests core functionality without requiring external services.

### 2. **Full Unit Test Suite**
```bash
python run_tests.py unit
```
Runs comprehensive unit tests with mocked services.

### 3. **Interactive Demo**
```bash
python demo_game_service.py
```
Shows the GameService in action with sample data.

## 📋 Testing Strategy Overview

### **Testing Pyramid**
```
    🔺 E2E Tests (Few, Slow)
   🔺🔺 Integration Tests (Some, Medium)
  🔺🔺🔺 Unit Tests (Many, Fast)
```

### **Test Categories**
1. **Unit Tests** - Test individual methods in isolation
2. **Integration Tests** - Test service interactions
3. **Performance Tests** - Validate real-time requirements
4. **Error Handling Tests** - Ensure graceful degradation

## 🧩 Unit Testing

### **What to Test**
- ✅ **Service Initialization** - Component loading and validation
- ✅ **Word Validation** - Dictionary lookup and frequency integration
- ✅ **Frequency Calculations** - Rank categorization and scoring
- ✅ **Suggestion Creation** - Transformation data processing
- ✅ **Chain Analysis** - Word chain statistics and summaries
- ✅ **Error Handling** - Invalid inputs and service failures

### **Mock Strategy**
```python
@patch('game_service.get_enhanced_scoring_service')
@patch('game_service.get_efficient_word_service')
async def test_method(self, mock_word, mock_scoring):
    # Mock service responses
    mock_scoring.return_value = AsyncMock()
    mock_word.return_value = AsyncMock()
    
    # Test method behavior
    result = await self.game_service.method()
    assert result["status"] == "expected"
```

## 🔗 Integration Testing

### **Service Dependencies**
- `enhanced_scoring_service` - ML scoring engine
- `efficient_word_service` - Word transformations
- `optimized_storage_service` - Probability tree storage
- `redis_connection` - Caching and state management

### **Integration Test Setup**
```bash
# 1. Ensure ML engine services are running
cd ml_engine
python -m services.enhanced_scoring_service

# 2. Run integration tests
python run_tests.py integration
```

### **What Integration Tests Validate**
- ✅ **Service Communication** - Correct method calls and responses
- ✅ **Data Flow** - End-to-end data transformation
- ✅ **Error Propagation** - Service failures handled correctly
- ✅ **State Consistency** - Game state remains valid

## ⚡ Performance Testing

### **Real-Time Requirements**
- **Word Validation**: < 10ms per word
- **Frequency Lookup**: < 5ms per word
- **Suggestion Generation**: < 100ms per batch
- **Game State Updates**: < 50ms per move

### **Performance Test Execution**
```bash
python run_tests.py performance
```

### **Benchmark Validation**
```python
async def test_performance_benchmarks(self):
    # Benchmark word validation
    start_time = time.time()
    for i in range(100):
        self.game_service._is_valid_word(f"word_{i}")
    validation_time = time.time() - start_time
    
    # Performance assertions
    assert validation_time < 0.1, f"Too slow: {validation_time:.3f}s"
```

## 🎯 Test-Driven Development

### **Red-Green-Refactor Cycle**
1. **Red** - Write failing test for new feature
2. **Green** - Implement minimal code to pass test
3. **Refactor** - Clean up code while maintaining tests

### **Example TDD Workflow**
```python
# 1. Write test first
async def test_new_feature(self):
    result = await self.game_service.new_feature("input")
    assert result["status"] == "success"
    assert "expected_data" in result

# 2. Run test (should fail)
# 3. Implement feature
# 4. Run test (should pass)
# 5. Refactor if needed
```

## 🔍 Test Coverage

### **Coverage Requirements**
- **Line Coverage**: > 90%
- **Branch Coverage**: > 85%
- **Function Coverage**: 100%

### **Coverage Report Generation**
```bash
python run_tests.py coverage
```

### **Coverage Analysis**
```bash
# View HTML report
open htmlcov/index.html

# View terminal report
python run_tests.py coverage
```

## 🚨 Error Testing

### **Error Scenarios to Test**
1. **Service Failures**
   - Scoring service unavailable
   - Word service errors
   - Storage service failures

2. **Invalid Inputs**
   - Empty words
   - Non-string inputs
   - Words not in dictionary

3. **State Errors**
   - Uninitialized service
   - No active game
   - Invalid game state

### **Error Handling Validation**
```python
async def test_error_handling(self):
    # Test uninitialized service
    with pytest.raises(GameServiceError) as exc_info:
        await self.game_service.start_game("cat")
    assert "not initialized" in str(exc_info.value)
```

## 📊 Test Data Management

### **Test Frequencies**
```python
test_frequencies = {
    "cat": 1e-05,      # common
    "hat": 2e-06,      # uncommon
    "bat": 3e-06,      # uncommon
    "rat": 1e-06,      # uncommon
    "sat": 5e-07,      # rare
    "mat": 2e-07,      # rare
}
```

### **Mock Transformations**
```python
mock_transformations = Mock()
mock_transformations.perfect_rhymes = ["hat", "bat", "rat"]
mock_transformations.rich_rhymes = ["sat", "mat"]
mock_transformations.anagrams = ["act", "tac"]
```

## 🧪 Testing Best Practices

### **Test Organization**
- **One assertion per test** - Clear failure identification
- **Descriptive test names** - Explain what is being tested
- **Setup/teardown methods** - Clean test environment
- **Mock external dependencies** - Isolate unit under test

### **Test Data**
- **Use realistic data** - Mimic production scenarios
- **Test edge cases** - Boundary conditions and error states
- **Avoid hard-coded values** - Use constants and fixtures

### **Async Testing**
```python
@pytest.mark.asyncio
async def test_async_method(self):
    result = await self.game_service.async_method()
    assert result["status"] == "success"
```

## 🔧 Testing Tools

### **Required Packages**
```bash
pip install -r test_requirements.txt
```

### **Key Dependencies**
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking utilities
- `pytest-cov` - Coverage reporting

### **IDE Integration**
- **VS Code**: Install Python Test Explorer extension
- **PyCharm**: Built-in pytest support
- **Vim/Emacs**: Use pytest command line

## 📈 Continuous Testing

### **Pre-commit Hooks**
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### **CI/CD Integration**
```yaml
# .github/workflows/test.yml
- name: Run Tests
  run: |
    cd ml_engine
    python run_tests.py all
```

## 🚨 Common Testing Issues

### **Import Errors**
```bash
# Add ml_engine to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/wurdo/ml_engine"
```

### **Async Test Failures**
```python
# Ensure proper async test decorator
@pytest.mark.asyncio
async def test_async_method(self):
    # Test implementation
```

### **Mock Configuration**
```python
# Mock service factory functions
@patch('game_service.get_enhanced_scoring_service')
async def test_method(self, mock_service):
    mock_service.return_value = AsyncMock()
    # Test implementation
```

## 📚 Testing Resources

### **Documentation**
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Guide](https://pytest-asyncio.readthedocs.io/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)

### **Examples**
- `test_game_service.py` - Complete test suite
- `demo_game_service.py` - Interactive testing
- `run_tests.py` - Test runner utility

## 🎯 Testing Checklist

### **Before Running Tests**
- [ ] Install test dependencies: `pip install -r test_requirements.txt`
- [ ] Set Python path: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`
- [ ] Verify ML engine structure is intact

### **Test Execution**
- [ ] Run basic tests: `python run_tests.py basic`
- [ ] Run unit tests: `python run_tests.py unit`
- [ ] Run performance tests: `python run_tests.py performance`
- [ ] Generate coverage report: `python run_tests.py coverage`

### **Quality Gates**
- [ ] All tests pass
- [ ] Coverage > 90%
- [ ] Performance benchmarks met
- [ ] No critical errors in logs

## 🚀 Next Steps

1. **Run the demo** to see GameService in action
2. **Execute basic tests** to verify core functionality
3. **Run full test suite** to catch integration issues
4. **Generate coverage report** to identify untested code
5. **Add new tests** for any new features or edge cases

---

**Remember**: Good testing is not about writing tests - it's about writing testable code and using tests to drive better design decisions.
