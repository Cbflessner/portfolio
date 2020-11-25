from redis import Redis

r = Redis(host="redis_1",port=7001, decode_responses=True)
redis_key = "test key"
redis_value = "test value"
hold=r.zincrby(redis_key,1, redis_value)
print("message sent to redis")
