import time
import redis


rc = redis.Redis(host='redis_1', port=6379)

rc.SET("foo", "bar")
