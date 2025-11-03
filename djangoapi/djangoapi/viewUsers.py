from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

def notLoggedIn(request):
    return JsonResponse({"ok":"false","message": "You are not logged in", "data":""})

@method_decorator(csrf_exempt, name='dispatch')
class AppLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"ok": True, "message": f"Prijava uspešna za {username}"})
        else:
            return Response({"ok": False, "message": "Neveljavno uporabniško ime ali geslo"})
    
class AppLogout(APIView):
    def post(self, request):
        print(request.user.username)
        if request.user.is_authenticated:
            username=request.user.username
            logout(request) #removes from the header of the request 
                #the user data, stored in a cookie
            return JsonResponse({"ok":"true","message": "The user {0} is now logged out".format(username), "data":[]})
        else:
            return JsonResponse({"ok":"false","message": "You where  not logged in", "data":[]})


         

