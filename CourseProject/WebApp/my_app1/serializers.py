from collections import OrderedDict
from rest_framework import serializers
from .models import Product, CustomUser, AuthUser, Application


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["pk", "name", "description", "country",
                  "quantity", "price", "pictures_url",
                  "id_category", "deleted_at"]
        
        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields


class ApplicationSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=False, required=False)
    is_progress = serializers.BooleanField(default=False, required=False)
    is_close = serializers.BooleanField(default=False, required=False)
    is_draft = serializers.BooleanField(default=False, required=False)
    is_reject = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = Application
        fields = ["pk", "created_at", "deleted_at", "is_active", "is_progress",
                  "is_close", "is_draft", "is_reject", "id_product", "quantity_product"]


class FullStockSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ["pk", "name", "description", "country",
                  "quantity", "price", "pictures_url",
                  "id_category", "deleted_at"]


class CustomUserSerializer(serializers.ModelSerializer):
    is_superuser = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = CustomUser
        fields = ['pk', 'email', 'password', 'is_superuser',
                  "created_at", "deleted_at", "updated_at"]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
