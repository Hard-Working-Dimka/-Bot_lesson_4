import redis

def connect_to_db():
    db = redis.Redis(
        host='redis-14096.c56.east-us.azure.redns.redis-cloud.com',
        port=14096,
        decode_responses=True,
        username="default",
        password="fw5LbJgqaYKkMnuiy3HaLxZ3Ly0beumI",
    )
    return db

# success = r.set('foo', 'bar')
# # True
#
# result = r.get('foo')
# print(result)
# # >>> bar

