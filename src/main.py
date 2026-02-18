"""
PayWatch - Main Application
"""
import asyncio
import signal
import sys
from pathlib import Path

from src.utils.logger import logger, setup_logger
from src.monitors.simple_checker import SimpleHealthChecker
from src.config import load_config


class PayWatch:
    """Main PayWatch application"""
    
    def __init__(self, config_path: str = 'config/config.yml'):
        """
        Initialize application.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        
        # Update logger level
        global logger
        logger = setup_logger(level=self.config.log_level)
        
        # Initialize checkers from config
        self.checkers = []
        for endpoint_config in self.config.endpoints:
            checker = SimpleHealthChecker(
                name=endpoint_config.name,
                url=endpoint_config.url,
                timeout=endpoint_config.timeout
            )
            # Store config for later use
            checker.config = endpoint_config
            self.checkers.append(checker)
            
            logger.info(
                f"Registered endpoint: {endpoint_config.name} "
                f"({endpoint_config.url}, interval={endpoint_config.interval}s)"
            )
        
        self.running = False
        logger.info(f"PayWatch initialized with {len(self.checkers)} endpoints")
    
    async def run_checks(self):
        """Run all checks once"""
        if not self.checkers:
            logger.warning("No endpoints configured!")
            return []
        
        logger.debug(f"Running {len(self.checkers)} health checks...")
        
        # Run all checks concurrently
        tasks = [checker.check() for checker in self.checkers]
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def run_monitoring_loop(self):
        """
        Main monitoring loop.
        
        Runs checks at configured intervals.
        """
        self.running = True
        
        # Print startup banner
        self._print_banner()
        
        # Track next check time for each checker
        import time
        next_check = {checker: 0 for checker in self.checkers}
        
        try:
            while self.running:
                current_time = time.time()
                
                # Check which monitors are due
                due_checkers = [
                    checker for checker in self.checkers
                    if current_time >= next_check[checker]
                ]
                
                if due_checkers:
                    # Run due checks
                    tasks = [checker.check() for checker in due_checkers]
                    await asyncio.gather(*tasks)
                    
                    # Update next check times
                    for checker in due_checkers:
                        next_check[checker] = current_time + checker.config.interval
                
                # Sleep a bit before checking again
                await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("\nShutdown requested...")
        finally:
            self.stop()
    
    def _print_banner(self):
        """Print startup banner"""
        print("\n" + "="*60)
        print(f"  PayWatch - {self.config.service_name}")
        print("="*60)
        print(f"  Monitoring: {len(self.checkers)} endpoints")
        print(f"  Metrics: {'Enabled' if self.config.metrics.enabled else 'Disabled'}")
        print(f"  Log level: {self.config.log_level}")
        print("\n  Press Ctrl+C to stop")
        print("="*60 + "\n")
    
    def stop(self):
        """Stop monitoring and print statistics"""
        self.running = False
        
        logger.info("\n" + "="*60)
        logger.info("Final Statistics")
        logger.info("="*60 + "\n")
        
        for checker in self.checkers:
            stats = checker.get_stats()
            logger.info(f"{stats['name']}:")
            logger.info(f"  Total checks: {stats['checks']}")
            logger.info(f"  Success rate: {stats['success_rate']}%")
            logger.info(f"  Avg response time: {stats['avg_response_time_ms']:.0f}ms")
            logger.info("")
        
        logger.info("PayWatch stopped")


def main():
    """Main entry point"""
    # Allow config path from command line
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config/config.yml'
    
    try:
        # Create and run application
        app = PayWatch(config_path)
        asyncio.run(app.run_monitoring_loop())
    
    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        logger.info("\nQuick fix:")
        logger.info("  cp config/config.example.yml config/config.yml")
        sys.exit(1)
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Goodbye!")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()