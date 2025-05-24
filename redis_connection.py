import redis


def connect_to_db(host, port, password):
    db = redis.Redis(
        host=host,
        port=port,
        decode_responses=True,
        password=password,
    )
    return db
