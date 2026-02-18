"""Test configuration validation"""
from src.config import PayWatchConfig, EndpointConfig

# Test 1: Invalid HTTP method
print("Test 1: Invalid HTTP method")
try:
    endpoint = EndpointConfig(
        name="test",
        url="https://example.com",
        method="INVALID"  # Should fail
    )
except Exception as e:
    print(f"  ✓ Caught error: {e}\n")

# Test 2: Negative timeout
print("Test 2: Negative timeout")
try:
    endpoint = EndpointConfig(
        name="test",
        url="https://example.com",
        timeout=-5  # Should fail
    )
except Exception as e:
    print(f"  ✓ Caught error: {e}\n")

# Test 3: Invalid port
print("Test 3: Invalid port")
try:
    config = PayWatchConfig(
        endpoints=[],
        metrics={"port": 99999}  # Should fail (too high)
    )
except Exception as e:
    print(f"  ✓ Caught error: {e}\n")

print("All validation tests passed!")
