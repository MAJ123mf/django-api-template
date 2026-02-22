# Django imports
from django.http import JsonResponse
from django.views import View
from django.forms.models import model_to_dict
from django.contrib.auth.mixins import LoginRequiredMixin

# Geoss
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import SnapToGrid

# rest_framework imports
from rest_framework import viewsets
from rest_framework import permissions

# My imports
from core.myLib.geometryTools import WkbConversor, GeometryChecks
from .models import Addresses
from .serializers import AddressSerializer
from buildings.models import Buildings
from djangoapi.settings import EPSG_FOR_GEOMETRIES, ST_SNAP_PRECISION, MAX_NUMBER_OF_RETRIEVED_ROWS
from core.myLib.baseDjangoView import BaseDjangoView


class HelloWord(View):
    def get(self, request):
        return JsonResponse({"ok": True, "message": "Hello world from app. Addresses", "data": []})


class AddressesView(LoginRequiredMixin, BaseDjangoView):
    """
    The get and post methods are defined in the BaseDjangoView. They forward the request
    to the methods selectone, selectall, insert, update, and delete, depending of the 
    action parameter in the URL.

    This class redefine the methods selectone, selectall, insert, update, and delete
    of the BaseDjangoView class to add a new action, insert2.
  
    To use this view:
    To get a record, the URL must be like:
        GET /addresses/addresses_view/selectone/<id>/
    To get all the records, the URL must be like:
        GET /addresses/addresses_view/selectall/
    To insert a record, the URL must be like:
        POST /addresses/addresses_view/insert/ --> The data must be sent in the body of the request.
    To update a record, the URL must be like:
        POST /addresses/addresses_view/update/<id>/ --> The data must be sent in the body of the request.
    To delete a record, the URL must be like:
        POST /addresses/addresses_view/delete/<id>/
    """
    
    def post(self, request, *args, **kwargs):
        """
        Redefines the post method of the BaseDjangoView class to add a new action.
        If the action is insert2, it will call the insert2 method.
        if not it will call the post method of the BaseDjangoView class.
        """
        action = kwargs.get('action')
        print(f"action child: {action}")

        if action == 'insert2':
            return self.insert2(request)
        else:            
            return super().post(request, *args, **kwargs)

    # GET OPERATIONS
    def selectone(self, id):
        l = list(Addresses.objects.filter(id=id))
        if len(l) == 0:
            return JsonResponse({'ok': False, "message": f"The address id {id} does not exist", "data": []}, status=200)
        a = l[0]
        d = model_to_dict(a)
        d['geom'] = a.geom.wkt
        return JsonResponse({'ok': True, 'message': 'Address Retrieved', 'data': [d]}, status=200)

    def selectall(self):
        l = Addresses.objects.all()[:MAX_NUMBER_OF_RETRIEVED_ROWS]
        data = []
        for a in l:
            d = model_to_dict(a)
            d['geom'] = a.geom.wkt
            data.append(d)
        return JsonResponse({'ok': True, 'message': 'Data retrieved', 'data': data}, status=200)

    # POST OPERATIONS
    def insert(self, request):
        """
        Inserts the point. Latter snap it to the grid. This must be done
        in the database. So we need to insert it before.
        After the address has been inserted:
            - snap it to grid
            - Check if the geometry is valid
            - Check if the point is within a building
            - Check if the point doesn't overlap with another address (same coordinates)
            - If any check fails, remove the row.
            - The only inconvenient is the id counter sums one more
        """
        print(f"Insert address")
        print(f"Request: {request.POST}")
        print(f"Request body: {request.body}")
        
        # Check if the geometry is present
        originalWkt = request.POST.get('geom', None)
        if originalWkt is None:
            return JsonResponse({'ok': False, 'message': 'The geometry is mandatory', 'data': []}, status=400)
        
        # Creates the geometry
        g = GEOSGeometry(request.POST.get('geom', ''), srid=EPSG_FOR_GEOMETRIES)
        print(f"Original geometry: {g}")

        # Check if it's a Point
        if g.geom_type != 'Point':
            return JsonResponse({'ok': False, 'message': 'The geometry must be a Point', 'data': []}, status=400)

        building_num = request.POST.get('building_num', None)
        street = request.POST.get('street', '') 
        house_num = request.POST.get('house_num', '')
        post_num = request.POST.get('post_num', None)
        post_name = request.POST.get('post_name', '')
        
        a = Addresses(
            building_num=building_num,
            street=street, 
            house_num=house_num,
            post_num=post_num,
            post_name=post_name,
            geom=g
        )
        a.save()
        print(f"Geometry inserted id: {a.id}")

        # Update the geometry to a snapped one to the grid
        Addresses.objects.filter(id=a.id).update(geom=SnapToGrid('geom', ST_SNAP_PRECISION))

        # Now we get a new object with the new geometry to perform the checks
        a = Addresses.objects.get(id=a.id)
        print('Snapped geometry', a.geom.wkt)
        
        # Check if geometry is valid
        valid = a.geom.valid
        print(f'Valid: {valid}')
        if not valid:
            print(f"Deleting invalid geometry {a.id}")
            a.delete()
            return JsonResponse({'ok': False, 'message': 'The geometry is not valid after the st_SnapToGrid', 'data': []}, status=200)   

        # Check if there's another address at the same location (overlapping points)
        filt = Addresses.objects.filter(geom__equals=a.geom).exclude(id=a.id)
        if filt.exists():
            n = filt.count()
            print(f"Deleting the address id {a.id}, as it overlaps with {n} other address(es)")
            a.delete()
            return JsonResponse({'ok': False, 'message': f'The address overlaps with {n} existing address(es) at the same location'}, status=200)

        # Check if the point is within a building
        buildings_containing = Buildings.objects.filter(geom__contains=a.geom)
        if not buildings_containing.exists():
            print(f"Deleting the address id {a.id}, as it is not within any building")
            a.delete()
            return JsonResponse({'ok': False, 'message': 'The address must be within a building polygon'}, status=200)
        
        # Create an address object from the model Addresses
        d = model_to_dict(a)
        d['geom'] = a.geom.wkt
        return JsonResponse({'ok': True, 'message': 'Address inserted', 'data': [d]}, status=201)

    def update(self, request, id):
        """
        On update you should also check the new geometry: snap it, check if it is valid,
        check if it is within a building, and check if it doesn't overlap with others except itself.
        
        Using the WkbConversor and GeometryChecks classes for consistency.
        """
        l = list(Addresses.objects.filter(id=id))
        if len(l) == 0:
            return JsonResponse({'ok': False, "message": f"The address id {id} does not exist", "data": []}, status=200)
        a = l[0]

        originalWkt = request.POST.get('geom', None)
        
        if originalWkt is not None:
            conversor = WkbConversor()
            wkb = conversor.set_wkt_from_text(originalWkt)
            newWkt = conversor.get_as_wkt()
            geojson = conversor.get_as_geojson()
            gc = GeometryChecks(wkb)
            isValid = gc.is_geometry_valid()

            print(f"Snapped wkt: {newWkt}")
            print(f"Snapped geojson: {geojson}")
            print(f"Snapped is valid: {isValid}")

            if not isValid:
                return JsonResponse({'ok': False, 'message': 'The geometry is not valid after the st_SnapToGrid', 'data': []}, status=200)   
            
            # Check geometry type
            polyGeos = GEOSGeometry(wkb)
            if polyGeos.geom_type != 'Point':
                return JsonResponse({'ok': False, 'message': 'The geometry must be a Point', 'data': []}, status=400)

            # Check if there's another address at the same location (excluding current one)
            overlapping = Addresses.objects.filter(geom__equals=polyGeos).exclude(id=id)
            if overlapping.exists():
                n = overlapping.count()
                return JsonResponse({'ok': False, 'message': f'The address overlaps with {n} existing address(es) at the same location', 'data': []}, status=200)

            # Check if the point is within a building
            buildings_containing = Buildings.objects.filter(geom__contains=polyGeos)
            if not buildings_containing.exists():
                return JsonResponse({'ok': False, 'message': 'The address must be within a building polygon', 'data': []}, status=200)

            # Update the address
            a.geom = wkb
            a.building_num = request.POST.get('building_num', None)
            a.street = request.POST.get('street', '')
            a.house_num = request.POST.get('house_num', '')
            a.post_num = request.POST.get('post_num', None)
            a.post_name = request.POST.get('post_name', '')
            a.save()
            
            d = model_to_dict(a)
            d['geom'] = conversor.get_as_wkt()  # snapped version
        else:
            return JsonResponse({'ok': False, 'message': 'Update. The geometry is mandatory', 'data': []}, status=200)
        
        return JsonResponse({'ok': True, 'message': "Address updated", 'data': [d]}, status=200)   

    def delete(self, request, id):
        l = list(Addresses.objects.filter(id=id))
        if len(l) == 0:
            return JsonResponse({'ok': False, "message": f"The address id {id} does not exist", "data": []}, status=200)
        a = l[0]
        a.delete()  
        return JsonResponse({'ok': True, "message": f"The address id {id} has been deleted", "data": []}, status=200)

    def insert2(self, request):
        """
        This method does the same as the insert method, 
        but by using the core/mylib/geometryTools.py module. 
        """
        originalWkt = request.POST.get('geom', None)
        
        if originalWkt is not None:
            conversor = WkbConversor()
            wkb = conversor.set_wkt_from_text(originalWkt)
            gc = GeometryChecks(wkb)
            isValid = gc.is_geometry_valid()

            if not isValid:
                return JsonResponse({'ok': False, 'message': 'The geometry is not valid after the st_SnapToGrid', 'data': []}, status=400)   
            
            # Check geometry type
            polyGeos = GEOSGeometry(wkb)
            if polyGeos.geom_type != 'Point':
                return JsonResponse({'ok': False, 'message': 'The geometry must be a Point', 'data': []}, status=400)

            # Check if there's another address at the same location
            overlapping = Addresses.objects.filter(geom__equals=polyGeos)
            if overlapping.exists():
                n = overlapping.count()
                return JsonResponse({'ok': False, 'message': f'The address overlaps with {n} existing address(es) at the same location', 'data': []}, status=400)

            # Check if the point is within a building
            buildings_containing = Buildings.objects.filter(geom__contains=polyGeos)
            if not buildings_containing.exists():
                return JsonResponse({'ok': False, 'message': 'The address must be within a building polygon', 'data': []}, status=400)
            
            a = Addresses()
            a.geom = wkb
            a.building_num = request.POST.get('building_num', None)
            a.street = request.POST.get('street', '')
            a.house_num = request.POST.get('house_num', '')
            a.post_num = request.POST.get('post_num', None)
            a.post_name = request.POST.get('post_name', '')
            a.save()
            
            d = model_to_dict(a)
            d['geom'] = a.geom.wkt
        else:
            return JsonResponse({'ok': False, 'message': 'The geometry is mandatory', 'data': []}, status=200)

        return JsonResponse({'ok': True, 'message': "Address Inserted", 'data': [d]}, status=200)   


class AddressesModelViewSet(viewsets.ModelViewSet):
    """
    DJANGO REST FRAMEWORK VIEWSET.

    The ModelViewSet class is a special view that Django Rest Framework 
    provides to handle the CRUD operations of a model
    
    The actions provided by the ModelViewSet class are:
        -list()  -> GET operation over /addresses/addresses/. It will return all records
        -retrieve() -> GET operation over /addresses/addresses/<id>/. 
                    It will return the record with the id.
        -create() -> POST operation over /addresses/addresses/. It will insert a new record
        -update() -> PUT operation over /addresses/addresses/<id>/. 
                    It will update the record with the id.
        -partial_update() -> PATCH operation over /addresses/addresses/<id>/. 
                It will update partially the record with the id.
                The difference between update and partial_update is that the first one
                will update all the fields of the record, while the second one will update
                only the fields that are present in the request.
        -destroy() -> DELETE operation over /addresses/addresses/<id>/. 
                It will delete the record with the id.
    """
    queryset = Addresses.objects.all().order_by('id')
    serializer_class = AddressSerializer           
    permission_classes = [permissions.AllowAny]  # Use https://rsinger86.github.io/drf-access-policy/
                                                 # for more advanced permissions management