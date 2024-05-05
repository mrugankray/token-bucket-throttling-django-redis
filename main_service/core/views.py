import traceback
import time
# 3rd party imports
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status

class HelloWorld(views.APIView):

    def get(self, request):
        try:
            # fake api call to some other endpoint
            time.sleep(25)
            # Process the request here
            return Response({'message': 'Hello World'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("ERROR:", traceback.print_exc())
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)