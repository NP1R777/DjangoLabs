import uuid
import redis
from .minio import add_pic
from WebApp import settings
from datetime import datetime
from .forms import SendTextForm
from django.http import HttpResponse
from rest_framework.views import APIView
from .permissions import IsManager, IsAdmin
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser, Product, Application
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .serializers import CustomUserSerializer, ProductSerializer, ApplicationSerializer
from rest_framework.decorators import permission_classes, authentication_classes, api_view


session_storage = redis.StrictRedis(host=settings.REDIS_HOST,
                                    port=settings.REDIS_PORT)

def GetOrders(request):
    elements = Product.objects.filter(deleted_at=None).values()
    return render(request, 'order_element.html', {"data": elements})


def GetOrder(request, id):
    order = Product.objects.filter(id=id).values()
    return render(request, 'order.html', {'data': order})


def order_ok(request, id):
    if request.method == "POST":
        form = SendTextForm(request.POST)
        if form.is_valid():
            quantity = int(form.cleaned_data['text'])
            
            product = get_object_or_404(Product, id=id)

            new_application = Application(is_active=True,
                                          id_product=product,
                                          quantity_product=quantity)
            new_application.save()
            return HttpResponseRedirect(f"/order_ok/{id}/")
        else:
            form = SendTextForm()
    
    return render(request, "order_ok.html")


def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator


class ApplicationList(APIView):
    model_class = Application
    serializer_class = ApplicationSerializer
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        pk = request.GET.get('pk')
        user = get_object_or_404(CustomUser, pk=pk)
        applications = self.model_class.objects.filter(
            pk__in=user.list_application, deleted_at=None
            ).order_by("pk")
        serializer = self.serializer_class(applications, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(request_body=ApplicationSerializer)
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            pk = request.data.get('pk_user')
            user = get_object_or_404(CustomUser, pk=pk)
            user.list_application.append(serializer.data.get('pk'))
            user.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplicationDetail(APIView):
    model_class = Application
    serializer_class = ApplicationSerializer

    def get(self, request, pk, format=None):
        application = get_object_or_404(Application, pk=pk)
        serializer = self.serializer_class(application)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        application = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        application = get_object_or_404(Application, pk=pk)
        application.deleted_at = datetime.now()
        application.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductList(APIView):
    model_class = Product
    serializer_class = ProductSerializer
    authentication_classes = []
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, requset, format=None):
        products = self.model_class.objects.filter(deleted_at=None)
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ProductSerializer)
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetail(APIView):
    model_class = Product
    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = []

    def get(self, request, pk, format=None):
        product = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(product)
        return Response(serializer.data)
    
    def post(self, request, pk, format=None):
        product = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        product = get_object_or_404(self.model_class, pk=pk)
        product.deleted_at = datetime.now()
        product.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @swagger_auto_schema(request_body=ProductSerializer)
    def put(self, request, pk, format=None):
        product = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(product, data=request.data, partial=True)
        if 'pic' in serializer.initial_data:
            pic_result = add_pic(product, serializer.initial_data['pic'])
            if 'error' in pic_result.data:
                return pic_result
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk, format=None):
        product = get_object_or_404(self.model_class, pk=pk)
        product.deleted_at = None
        product.save()
        return Response(status=status.HTTP_200_OK)


class AdminPanelProducts(APIView):
    model_class = Product
    serializer_class = ProductSerializer

    def get(self, request, format=None):
        products = self.model_class.objects.all()
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)


class UsersList(APIView):
    model_class = CustomUser
    serializers_class = CustomUserSerializer

    def get(self, request, format=None):
        users = self.model_class.objects.order_by("pk")
        serializer = self.serializers_class(users, many=True)
        return Response(serializer.data)


class UserDetail(APIView):
    model_class = CustomUser
    serializer_class = CustomUserSerializer

    def get(self, request, pk, format=None):
        user = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(user)
        return Response(serializer.data)
    
    def delete(self, request, pk, format=None):
        user = get_object_or_404(self.model_class, pk=pk)
        user.deleted_at = datetime.now()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, pk, format=None):
        user = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    model_class = CustomUser
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def create(self, request):
        if self.model_class.objects.filter(email=request.data['email']).exists():
            return Response({"status": "Exist"}, status=status.HTTP_409_CONFLICT)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            self.model_class.objects.create_user(email=serializer.data['email'],
                                                 password=serializer.data['password'],
                                                 is_superuser=serializer.data['is_superuser'])
            return Response({"status": "Success",
                             "data": {
                                 "email": serializer.data['email']
                             }}, status=status.HTTP_201_CREATED)
        return Response({"status": "Error", "error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
@csrf_exempt
@authentication_classes([])
@swagger_auto_schema(method='post', request_body=CustomUserSerializer)
@api_view(['Post'])
def login_view(request):
    email = request.data.get("email", None)
    password = request.data.get("password", None)
    user = authenticate(request=request, username=email, password=password)
    if user is not None:
        user_row = CustomUser.objects.filter(email=email).values('id', 'is_superuser', 'deleted_at').first()
        if not user_row or user_row.get('deleted_at') is not None:
            return Response({"status": "error", "error": "login failed"},
                            status=status.HTTP_401_UNAUTHORIZED)
        else:
            login(request, user)
            random_key = str(uuid.uuid4())
            session_storage.set(random_key, email)
            return Response({"status": 'Success',
                            "pk": user_row.get('id'),
                            "is_superuser": user_row.get('is_superuser')}, status=200)
    else:
        return Response({"status": "error", "error": "login failed"},
                        status=status.HTTP_401_UNAUTHORIZED)

@api_view(['Post'])
def logout_view(request):
    logout(request._request)
    return Response({'status': 'Success'}, status=200)
