import traceback
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

# import from utils
from core.utils import make_requests

class ReleaseTokenMiddleware(MiddlewareMixin):    
    def process_response(self, request, response):
        try:
            client_ip = request.META.get('HTTP_X_REAL_IP')
            if not client_ip:
                return JsonResponse({'error': 'X-Real-IP header not found'}, status=400)
            
            # Get token from request header
            token = request.META.get('HTTP_REQ_TOKEN')
            if not token:
                return JsonResponse({'error': "Req-Token not found in headers"}, status=400)
            
            # Make a request to the check_token endpoint
            response_token, status_code = make_requests('http://tokenservice:8000/api/release_token', {'X-Real-IP': client_ip, 'Req-Token': token})
            
            # Check if the token is valid
            if status_code < 300: # 200-299 is accepted
                return response
            else:
                print("ERROR: ", response_token)
                # Token is invalid, return an error response
                return JsonResponse(response_token, status=status_code)

        except Exception as e:
            print("ERROR:", traceback.print_exc())
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
        
class CheckTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            client_ip = request.META.get('HTTP_X_REAL_IP')
            if not client_ip:
                return JsonResponse({'error': 'X-Real-IP header not found'}, status=400)
            
            # Make a request to the check_token endpoint
            response_token, status_code = make_requests('http://tokenservice:8000/api/check_token', {'X-Real-IP': client_ip})
            
            # Check if the token is valid
            if status_code < 300: # 200-299 is accepted
                request.META["HTTP_REQ_TOKEN"] = response_token["token"]

                # Pass request to the next middleware or view
                response = self.get_response(request)
                return response
            else:
                print("ERROR: ", response_token)
                # Token is invalid, return an error response
                return JsonResponse(response_token, status=status_code)

        except Exception as e:
            print("ERROR:", traceback.print_exc())
            return JsonResponse({'error': 'Internal Server Error'}, status=500)     
        
