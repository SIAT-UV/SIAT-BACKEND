from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import AccidenteSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class AccidenteCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Para manejar archivos


    def post(self, request, format=None):
        serializer = AccidenteSerializer(data=request.data)
        if serializer.is_valid():
            # Se asigna el usuario autenticado (instancia de Usuario)
            accidente = serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



