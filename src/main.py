"""
PayWatch 
Main application entry point
"""
import asyncio
import signal
import sys

from src.utils.logger import logger
from src.monitors.simple_checker import SimpleHealthChecker


class PayWatch:
    """Main PayWatch application"""
    
    def __init__(self):
        """Initialize application"""
        self.checkers = []
        self.running = False
    
    def add_checker(self, name, url, timeout=5):
        """
        Add a health checker.
        
        Args:
            name: Checker name
            url: URL to check
            timeout: Timeout in seconds
        """
        checker = SimpleHealthChecker(name, url, timeout)
        self.checkers.append(checker)
        logger.info(f"Added checker: {name} -> {url}")
    
    async def run_checks(self):
        """Run all checks once"""
        if not self.checkers:
            logger.warning("No checkers configured!")
            return
        
        logger.info(f"Running {len(self.checkers)} checks...")
        
        # Run all checks concurrently
        tasks = [checker.check() for checker in self.checkers]
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def run_forever(self, interval=60):
        """
        Run checks continuously.
        
        Args:
            interval: Seconds between check cycles
        """
        self.running = True
        
        logger.info(f"Starting monitoring (interval: {interval}s)")
        logger.info("Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                # Run checks
                await self.run_checks()
                
                # Wait before next cycle
                logger.info(f"\nWaiting {interval}s until next check...\n")
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("\nShutdown requested...")
            self.stop()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        
        # Print final statistics
        logger.info("\n" + "="*60)
        logger.info("Final Statistics")
        logger.info("="*60 + "\n")
        
        for checker in self.checkers:
            stats = checker.get_stats()
            logger.info(f"{stats['name']}:")
            logger.info(f"  Total checks: {stats['checks']}")
            logger.info(f"  Successes: {stats['successes']}")
            logger.info(f"  Failures: {stats['failures']}")
            logger.info(f"  Success rate: {stats['success_rate']}%")
            logger.info(f"  Avg response time: {stats['avg_response_time_ms']:.0f}ms")
            logger.info("")
        
        logger.info("PayWatch stopped")


def main():
    """Main entry point"""
    # Create application
    app = PayWatch()
    
    # Add some endpoints to monitor
    app.add_checker("Google", "https://www.google.com")
    app.add_checker("GitHub", "https://github.com")
    app.add_checker("HTTPBin OK", "https://httpbin.org/status/200")
    app.add_checker("HTTPBin Slow", "https://httpbin.org/delay/2")
    app.add_checker("My Portfolio", "https://me-lita.onrender.com/")
    app.add_checker("Slow", "https://httpbin.org/delay/10")
    app.add_checker("Fake", "https://this-does-not-exist-xyz123.com")
    
    # Run monitoring
    try:
        asyncio.run(app.run_forever(interval=30))
    except KeyboardInterrupt:
        logger.info("Goodbye!")


if __name__ == "__main__":
    main()