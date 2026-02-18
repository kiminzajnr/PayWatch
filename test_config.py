"""Test configuration loading"""
from src.config import load_config

# This should fail (file doesn't exist yet)
try:
    config = load_config('config/config.yml')
except FileNotFoundError as e:
    print(f"Expected error: {e}")
    print("\nLet's create the config file...")

# Copy example config
import shutil
shutil.copy('config/config.example.yml', 'config/config.yml')

# Now it should work
config = load_config('config/config.yml')

print(f"\n✓ Configuration loaded successfully!")
print(f"  Service name: {config.service_name}")
print(f"  Log level: {config.log_level}")
print(f"  Endpoints: {len(config.endpoints)}")
print(f"  Metrics enabled: {config.metrics.enabled}")

# Print each endpoint
print("\nEndpoints:")
for ep in config.endpoints:
    print(f"  - {ep.name}: {ep.url}")
    print(f"    Method: {ep.method}, Timeout: {ep.timeout}s")
    print(f"    Interval: {ep.interval}s, Expected: {ep.expected_status}")
    print(f"    Max response time: {ep.expected_response_time}ms")
