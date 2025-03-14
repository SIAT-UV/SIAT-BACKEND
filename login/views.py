from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import RegistroUsuarioSerializer
# Create your views here.


@api_view(['POST'])
def registro_api(request):
    serializer = RegistroUsuarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Usuario registrado correctamente"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
