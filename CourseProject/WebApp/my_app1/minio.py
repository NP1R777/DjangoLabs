from minio import Minio
from WebApp import settings
from rest_framework.response import *
from django.core.files.uploadedfile import InMemoryUploadedFile


def process_file_upload(file_object: InMemoryUploadedFile,
                        client, image_name):
    try:
        client.put_object('logo', image_name, file_object, file_object.size)
        return f"http://localhost:9000/logo/pictures/{image_name}"
    except Exception as e:
        return {"error": str(e)}


def add_pic(new_product, pic):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    i = new_product.id
    img_obj_name = f"{i}.png"

    if not pic:
        return Response({"error": "Нет файла для изображения логотипа"})
    result = process_file_upload(pic, client, img_obj_name)

    if 'error' in result:
        return Response(result)
    
    new_product.pictures_url = result
    new_product.save()

    return Response({"message": "success"})






# class Images{
#     private string url;
#     string ImageName {get; set;}
#     string ImgaeURL {get => url;
#                      set => $"addr{}" }
# }