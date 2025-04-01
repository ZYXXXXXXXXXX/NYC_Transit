import time


class SimpleCache:
   """
   Simple in-memory cache implementation
   """

   def __init__(self):
       self.cache = {}  # Cache data storage
       self.timestamps = {}  # Timestamp storage

   def get(self, key, timeout=60):
       """
       Get cached data

       Args:
           key (str): Cache key
           timeout (int): Timeout in seconds

       Returns:
           any: Cached data or None if not found/expired
       """
       # Check if key exists
       if key not in self.cache:
           return None

       # Check if expired
       current_time = time.time()
       if current_time - self.timestamps[key] > timeout:
           # Remove expired data
           self.remove(key)
           return None

       return self.cache[key]

   def set(self, key, value):
       """
       Set cache data

       Args:
           key (str): Cache key
           value (any): Data to cache
       """
       self.cache[key] = value
       self.timestamps[key] = time.time()

   def remove(self, key):
       """
       Remove specific cache entry

       Args:
           key (str): Cache key to remove
       """
       if key in self.cache:
           del self.cache[key]
           del self.timestamps[key]

   def clear(self):
       """Clear all cache"""
       self.cache = {}
       self.timestamps = {}

   def get_stats(self):
       """
       Get cache statistics

       Returns:
           dict: Dictionary with cache stats
       """
       return {
           "total_keys": len(self.cache),
           "keys": list(self.cache.keys())
       }


# Create global cache instance
cache = SimpleCache()