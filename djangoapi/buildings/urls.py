from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'buildings', views.BuildingsModelViewSet)
router.register(r'owners', views.OwnersModelViewSet)

urlpatterns = [
    path("hello_world/", views.HelloWord.as_view(), name="hello_world"),  # http://localhost:8000/buildings/hello_world/
    
    # BuildingsView - custom view with GET and POST operations
    path('buildings_view/selectone/<int:id>/', views.BuildingsView.as_view(), {'action': 'selectone'}, name='buildings_view_selectone'),  # GET
    path('buildings_view/selectall/', views.BuildingsView.as_view(), {'action': 'selectall'}, name='buildings_view_selectall'),  # GET
    path('buildings_view/insert/', views.BuildingsView.as_view(), {'action': 'insert'}, name='buildings_view_insert'),  # POST
    path('buildings_view/insert2/', views.BuildingsView.as_view(), {'action': 'insert2'}, name='buildings_view_insert2'),  # POST
    path('buildings_view/update/<int:id>/', views.BuildingsView.as_view(), {'action': 'update'}, name='buildings_view_update'),  # POST
    path('buildings_view/delete/<int:id>/', views.BuildingsView.as_view(), {'action': 'delete'}, name='buildings_view_delete'),  # POST
    
    # REST Framework router URLs (BuildingsModelViewSet and OwnersModelViewSet)
    path('', include(router.urls)),                                        
]


# Custom BuildingsView:
# 
# GET /buildings/buildings_view/selectone/<id>/ - pridobi eno stavbo
# GET /buildings/buildings_view/selectall/ - pridobi vse stavbe
# POST /buildings/buildings_view/insert/ - vstavi stavbo (način 1)
# POST /buildings/buildings_view/insert2/ - vstavi stavbo (način 2 z geometryTools)
# POST /buildings/buildings_view/update/<id>/ - posodobi stavbo
# POST /buildings/buildings_view/delete/<id>/ - izbriši stavbo
# 
# REST Framework (BuildingsModelViewSet):
# 
# GET /buildings/buildings/ - list() - vse stavbe
# GET /buildings/buildings/<id>/ - retrieve() - ena stavba
# POST /buildings/buildings/ - create() - vstavi
# PUT /buildings/buildings/<id>/ - update() - posodobi
# PATCH /buildings/buildings/<id>/ - partial_update() - delna posodobitev
# DELETE /buildings/buildings/<id>/ - destroy() - izbriši
#
# REST Framework (OwnersModelViewSet):
# 
# GET /buildings/owners/ - list() - vsi lastniki
# GET /buildings/owners/<id>/ - retrieve() - en lastnik
# POST /buildings/owners/ - create() - vstavi
# PUT /buildings/owners/<id>/ - update() - posodobi
# PATCH /buildings/owners/<id>/ - partial_update() - delna posodobitev
# DELETE /buildings/owners/<id>/ - izbriši