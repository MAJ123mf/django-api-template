from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'roads', views.RoadsModelViewSet)

urlpatterns = [
    path("hello_world/", views.HelloWord.as_view(), name="hello_world"),  # http://localhost:8000/roads/hello_world/
    
    # RoadsView - custom view with GET and POST operations
    path('roads_view/selectone/<int:id>/', views.RoadsView.as_view(), {'action': 'selectone'}, name='roads_view_selectone'),  # GET
    path('roads_view/selectall/', views.RoadsView.as_view(), {'action': 'selectall'}, name='roads_view_selectall'),  # GET
    path('roads_view/insert/', views.RoadsView.as_view(), {'action': 'insert'}, name='roads_view_insert'),  # POST
    path('roads_view/insert2/', views.RoadsView.as_view(), {'action': 'insert2'}, name='roads_view_insert2'),  # POST
    path('roads_view/update/<int:id>/', views.RoadsView.as_view(), {'action': 'update'}, name='roads_view_update'),  # POST
    path('roads_view/delete/<int:id>/', views.RoadsView.as_view(), {'action': 'delete'}, name='roads_view_delete'),  # POST
    
    # REST Framework router URLs (RoadsModelViewSet)
    path('', include(router.urls)),                                        
]


# Custom RoadsView:
# 
# GET /roads/roads_view/selectone/<id>/ - pridobi eno cesto
# GET /roads/roads_view/selectall/ - pridobi vse ceste
# POST /roads/roads_view/insert/ - vstavi cesto (način 1)
# POST /roads/roads_view/insert2/ - vstavi cesto (način 2 z geometryTools)
# POST /roads/roads_view/update/<id>/ - posodobi cesto
# POST /roads/roads_view/delete/<id>/ - izbriši cesto
# 
# REST Framework (RoadsModelViewSet):
# 
# GET /roads/roads/ - list() - vse ceste
# GET /roads/roads/<id>/ - retrieve() - ena cesta
# POST /roads/roads/ - create() - vstavi
# PUT /roads/roads/<id>/ - update() - posodobi
# PATCH /roads/roads/<id>/ - partial_update() - delna posodobitev
# DELETE /roads/roads/<id>/ - destroy() - izbriši