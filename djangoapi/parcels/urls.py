from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'parcels', views.ParcelsModelViewSet)
router.register(r'parcelsowners', views.ParcelOwnersModelViewSet)

# URL patterns
urlpatterns = [
    # Pozdravna stran
    path('hello/', views.HelloWord.as_view(), name='hello'),
    
    # Logout
    path('logout/', views.custom_logout_view, name='logout'),
    
    # ParcelsView - CRUD operacije
    path('parcels_view/selectone/<int:id>/', views.ParcelsView.as_view(), name='parcels-selectone'),
    path('parcels_view/selectall/', views.ParcelsView.as_view(), name='parcels-selectall'),
    path('parcels_view/insert/', views.ParcelsView.as_view(), name='parcels-insert'),
    path('parcels_view/insert2/', views.ParcelsView.as_view(), name='parcels-insert2'),
    path('parcels_view/update/<int:id>/', views.ParcelsView.as_view(), name='parcels-update'),
    path('parcels_view/delete/<int:id>/', views.ParcelsView.as_view(), name='parcels-delete'),
    
    # ViewSet URL-ji (REST framework)
    path('', include(router.urls)),
]


"""1. OSNOVNI ENDPOINTI
--------------------
GET  http://localhost:8000/parcels/hello/
GET  http://localhost:8000/parcels/logout/

2. PARCELSVIEW (CUSTOM VIEW)
-----------------------------
GET  http://localhost:8000/parcels/parcels_view/selectone/1/
GET  http://localhost:8000/parcels/parcels_view/selectall/
POST http://localhost:8000/parcels/parcels_view/insert/
POST http://localhost:8000/parcels/parcels_view/insert2/
POST http://localhost:8000/parcels/parcels_view/update/1/
POST http://localhost:8000/parcels/parcels_view/delete/1/

3. PARCELSMODELVIEWSET (REST FRAMEWORK)
----------------------------------------
GET    http://localhost:8000/parcels/parcels/
GET    http://localhost:8000/parcels/parcels/1/
POST   http://localhost:8000/parcels/parcels/
PUT    http://localhost:8000/parcels/parcels/1/
PATCH  http://localhost:8000/parcels/parcels/1/
DELETE http://localhost:8000/parcels/parcels/1/

4. PARCELOWNERSMODELVIEWSET (REST FRAMEWORK)
---------------------------------------------
GET    http://localhost:8000/parcels/owners/
GET    http://localhost:8000/parcels/owners/1/
POST   http://localhost:8000/parcels/owners/
PUT    http://localhost:8000/parcels/owners/1/
PATCH  http://localhost:8000/parcels/owners/1/
DELETE http://localhost:8000/parcels/owners/1/
"""