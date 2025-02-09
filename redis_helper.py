import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

main_db = {
    "101": {"name": "iPhone 14", "price": "999", "stock": "50"},
    "102": {"name": "MacBook Pro", "price": "1999", "stock": "20"},
    "103": {"name": "AirPods", "price": "199", "stock": "100"}
}

cache_ttl=60

def get_product_redis(product_id):
    # Check Redis cache
    print(f"Checking Redis for product ID: {product_id}")
    product = redis_client.hgetall(f"product:{product_id}")
    
    if product:
        print(f"Cache hit: Product {product_id} found in Redis")
        return product, "cache"

    # Cache miss, check main database
    print(f"Cache miss: Product {product_id} not found in Redis. Checking main database.")
    if product_id in main_db:
        product = main_db[product_id]
        print(f"Product {product_id} found in main database. Caching it in Redis.")
        
        # Cache the product correctly
        redis_client.hset(f"product:{product_id}", mapping=product)
        redis_client.expire(f"product:{product_id}", cache_ttl)  # Set TTL
        
        print(f"Product {product_id} cached in Redis with TTL {cache_ttl} seconds.")
        return product, "main_db"

    # Product not found in both cache and database
    print(f"Product {product_id} not found in both Redis and main database.")
    return None, None  # Return None if product is not found

