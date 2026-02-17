"""
Simple health checker
"""
import asyncio
import time
from datetime import datetime
import aiohttp

from src.utils.logger import logger


class SimpleHealthChecker:
    """
    Checks if a URL is reachable and measures response time.
    
    """
    
    def __init__(self, name, url, timeout=5):
        """
        Initialize health checker.
        
        Args:
            name: Friendly name for this check (e.g., "Payment API")
            url: URL to check
            timeout: Timeout in seconds
        """
        self.name = name
        self.url = url
        self.timeout = timeout
        
        # Statistics
        self.check_count = 0
        self.success_count = 0
        self.total_response_time = 0.0
    
    async def check(self):
        """
        Perform a health check.
        
        Returns:
            dict with results
        """
        start_time = time.time()
        
        try:
            # Create HTTP session
            async with aiohttp.ClientSession() as session:
                # Make request
                async with session.get(
                    self.url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    # Calculate response time
                    elapsed_ms = (time.time() - start_time) * 1000
                    
                    # Update statistics
                    self.check_count += 1
                    self.total_response_time += elapsed_ms
                    
                    # Check if successful
                    is_success = response.status == 200
                    if is_success:
                        self.success_count += 1
                    
                    # Determine health status
                    if response.status == 200:
                        if elapsed_ms < 500:
                            status = "healthy"
                        else:
                            status = "degraded"  # Slow but working
                    else:
                        status = "unhealthy"
                    
                    # Log result
                    if status == "healthy":
                        logger.info(
                            f"✓ {self.name}: {status} "
                            f"({response.status}, {elapsed_ms:.0f}ms)"
                        )
                    else:
                        logger.warning(
                            f"⚠ {self.name}: {status} "
                            f"({response.status}, {elapsed_ms:.0f}ms)"
                        )
                    
                    return {
                        'name': self.name,
                        'status': status,
                        'status_code': response.status,
                        'response_time_ms': elapsed_ms,
                        'timestamp': datetime.utcnow().isoformat(),
                        'success': is_success,
                    }
        
        except asyncio.TimeoutError:
            elapsed_ms = (time.time() - start_time) * 1000
            self.check_count += 1
            
            logger.error(f"✗ {self.name}: timeout after {elapsed_ms:.0f}ms")
            
            return {
                'name': self.name,
                'status': 'unhealthy',
                'error': 'timeout',
                'response_time_ms': elapsed_ms,
                'timestamp': datetime.utcnow().isoformat(),
                'success': False,
            }
        
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            self.check_count += 1
            
            logger.error(f"✗ {self.name}: error - {str(e)}")
            
            return {
                'name': self.name,
                'status': 'unhealthy',
                'error': str(e),
                'response_time_ms': elapsed_ms,
                'timestamp': datetime.utcnow().isoformat(),
                'success': False,
            }
    
    def get_stats(self):
        """Get statistics for this checker."""
        if self.check_count == 0:
            return {
                'name': self.name,
                'checks': 0,
                'success_rate': 0,
                'avg_response_time_ms': 0,
            }
        
        success_rate = (self.success_count / self.check_count) * 100
        avg_time = self.total_response_time / self.check_count
        
        return {
            'name': self.name,
            'checks': self.check_count,
            'successes': self.success_count,
            'failures': self.check_count - self.success_count,
            'success_rate': round(success_rate, 2),
            'avg_response_time_ms': round(avg_time, 2),
        }