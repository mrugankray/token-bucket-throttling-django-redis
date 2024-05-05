import requests
import json

def make_requests(url, headers):
    # Make a request to the check_token endpoint
    check_token_response = requests.get(url=url, headers=headers)
    
    # Check if the token is valid
    if check_token_response.status_code < 300: # 200-299 is accepted
        body = check_token_response.text
        body_obj = json.loads(body)
        # request.META.set("Req-Token", body_obj["token"])

        # Pass request to the next middleware or view
        # response = self.get_response(request)
        # return response
        return body_obj, check_token_response.status_code
    else:
        error_body = check_token_response.text
        error_object = json.loads(error_body)
        # Token is invalid, return an error response
        # return JsonResponse(error_object, status=check_token_response.status_code)
        return error_object, check_token_response.status_code