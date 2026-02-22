
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import logout

from .pycode import users

def notLoggedIn(request):
    return JsonResponse({"ok":"false","message": "You are not logged in", "data":""})


class AppLogin(View):
    def post(self, request):
        r=users.appLogin(request)
        return JsonResponse(r)
    
class AppLogout(View):
    def post(self, request):
        print(request.user.username)
        if request.user.is_authenticated:
            username=request.user.username
            logout(request) #removes from the header of the request 
                #the user data, stored in a cookie
            return JsonResponse({"ok":"true","message": "The user {0} is now logged out".format(username), "data":[]})
        else:
            return JsonResponse({"ok":"false","message": "You where  not logged in", "data":[]})

