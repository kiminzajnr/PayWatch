import asyncio
from src.monitors.simple_checker import SimpleHealthChecker

async def main():
    # Create checkers
    checkers = [
        SimpleHealthChecker("Google", "https://www.google.com"),
        SimpleHealthChecker("GitHub", "https://github.com"),
        SimpleHealthChecker("HTTPBin", "https://httpbin.org/status/200"),
    ]
    
    # Run checks
    results = await asyncio.gather(*[c.check() for c in checkers])
    
    # Print statistics
    print("\n" + "="*50)
    print("Statistics:")
    print("="*50)
    for checker in checkers:
        stats = checker.get_stats()
        print(f"\n{stats['name']}:")
        print(f"  Checks: {stats['checks']}")
        print(f"  Success rate: {stats['success_rate']}%")
        print(f"  Avg response time: {stats['avg_response_time_ms']:.0f}ms")

asyncio.run(main())
