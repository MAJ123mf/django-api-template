from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'addresses', views.AddressesModelViewSet)

urlpatterns = [
    path("hello_world/", views.HelloWord.as_view(), name="hello_world"),  # http://localhost:8000/addresses/hello_world/
    
    # AddressesView - custom view with GET and POST operations
    path('addresses_view/selectone/<int:id>/', views.AddressesView.as_view(), {'action': 'selectone'}, name='addresses_view_selectone'),  # GET
    path('addresses_view/selectall/', views.AddressesView.as_view(), {'action': 'selectall'}, name='addresses_view_selectall'),  # GET
    path('addresses_view/insert/', views.AddressesView.as_view(), {'action': 'insert'}, name='addresses_view_insert'),  # POST
    path('addresses_view/insert2/', views.AddressesView.as_view(), {'action': 'insert2'}, name='addresses_view_insert2'),  # POST
    path('addresses_view/update/<int:id>/', views.AddressesView.as_view(), {'action': 'update'}, name='addresses_view_update'),  # POST
    path('addresses_view/delete/<int:id>/', views.AddressesView.as_view(), {'action': 'delete'}, name='addresses_view_delete'),  # POST
    
    # REST Framework router URLs (AddressesModelViewSet)
    path('', include(router.urls)),                                        
]


# Custom AddressesView:
# 
# GET /addresses/addresses_view/selectone/<id>/ - pridobi en naslov
# GET /addresses/addresses_view/selectall/ - pridobi vse naslove
# POST /addresses/addresses_view/insert/ - vstavi naslov (način 1)
# POST /addresses/addresses_view/insert2/ - vstavi naslov (način 2 z geometryTools)
# POST /addresses/addresses_view/update/<id>/ - posodobi naslov
# POST /addresses/addresses_view/delete/<id>/ - izbriši naslov
# 
# REST Framework (AddressesModelViewSet):
# 
# GET /addresses/addresses/ - list() - vsi naslovi
# GET /addresses/addresses/<id>/ - retrieve() - en naslov
# POST /addresses/addresses/ - create() - vstavi
# PUT /addresses/addresses/<id>/ - update() - posodobi
# PATCH /addresses/addresses/<id>/ - partial_update() - delna posodobitev
# DELETE /addresses/addresses/<id>/ - destroy() - izbriši