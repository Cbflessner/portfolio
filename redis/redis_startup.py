from rediscluster import RedisCluster
startup_nodes = [{"host": "10.0.0.11", "port": "7001"}]
rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)
rc.