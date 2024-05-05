import traceback
# 3rd party imports
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status

import redis
from redis import ConnectionPool

# constants
MAX_ALLOWED_TOKEN_PER_IP = 1

class CheckToken(views.APIView):

    def get(self, request):
        try:
            # Create a connection pool
            pool = ConnectionPool(host='redis', port=6379, db=0, max_connections=2)
            redis_conn = redis.StrictRedis(connection_pool=pool)

            # Checking for IP in headers
            client_ip = request.META.get('HTTP_X_REAL_IP')
            if not client_ip:
                return Response({'error': "Client IP not found in headers"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check the number of tokens for the client's IP address
            num_tokens = redis_conn.scard(client_ip)
            if num_tokens >= MAX_ALLOWED_TOKEN_PER_IP:
                return Response({"error": f"Client already has {MAX_ALLOWED_TOKEN_PER_IP} tokens"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # getting token & removing from set
            token = redis_conn.spop('available_tokens')
            if not token:
                return Response({'error': 'Server is too busy'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            token = token.decode('utf-8')
            # Store the token against the client IP in a Redis hash
            # Move the token to the client's IP address set
            redis_conn.sadd(client_ip, token) # not expiring because if we do that then the token would be gone too

            return Response({'token': token}, status=status.HTTP_200_OK)
                
        except Exception as e:
            print("ERROR:", traceback.print_exc())
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReleaseToken(views.APIView):

    def get(self, request):
        try:
            # Checking for IP in headers
            client_ip = request.META.get('HTTP_X_REAL_IP')
            if not client_ip or client_ip == "":
                return Response({'error': "Client IP not found in headers"}, status=status.HTTP_400_BAD_REQUEST)
        
            # Get token from request header
            token = request.META.get('HTTP_REQ_TOKEN')
            if not token:
                return Response({'error': "Req-Token not found in headers"}, status=status.HTTP_400_BAD_REQUEST)

            # Create a connection pool
            pool = ConnectionPool(host='redis', port=6379, db=0, max_connections=2)
            redis_conn = redis.StrictRedis(connection_pool=pool)

            # Removing token
            removed_count = redis_conn.srem(client_ip, token)

            # checks if 
            if not removed_count:
                return Response({'error': "Incorrect IP or Token passed"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Add token back to available_tokens list
            redis_conn.sadd('available_tokens', token)

            return Response({'message': "Token released successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            print("ERROR:", traceback.print_exc())
            return Response({'error': "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)