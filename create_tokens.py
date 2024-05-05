import redis
import random
import string

# Function to generate a random token
def generate_token(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Connect to Redis
redis_conn = redis.StrictRedis(host='localhost', port=6379, db=0)

# Number of tokens to generate
num_tokens = 2

# Generate and insert tokens into Redis sets
available_tokens = set()
unavailable_tokens = set()

for _ in range(num_tokens):
    token = generate_token()
    available_tokens.add(token)

# Add available tokens to Redis
redis_conn.sadd('available_tokens', *available_tokens)

# Display the tokens added to Redis
print("Available Tokens:", available_tokens)
