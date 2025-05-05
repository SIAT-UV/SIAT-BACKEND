from rest_framework.views import exception_handler
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and "detail" in response.data:
        mensaje = response.data["detail"]

        # Cambiar mensaje por defecto de credenciales no proporcionadas
        if mensaje == "Authentication credentials were not provided.":
            response.data = {"CODE_ERR": "AUTHENTICATION_CREDENTIALS_WERE_NOT_PROVIDED."}
            response.status_code = status.HTTP_403_FORBIDDEN 

        # También puedes personalizar otros mensajes aquí:
        elif mensaje == "Invalid token.":
            response.data = {"CODE_ERR": "INVALID_TOKEN."}
            response.status_code = status.HTTP_403_FORBIDDEN

        elif mensaje == "Given token not valid for any token type":
            response.data = {"CODE_ERR": "INVALID_TOKEN."}
            response.status_code = status.HTTP_401_UNAUTHORIZED
    
        elif mensaje == "Token is blacklisted":
            response.data = {"CODE_ERR": "TOKEN_IS_BLACKLISTED."}
            response.status_code = status.HTTP_401_UNAUTHORIZED
        # Mensaje cuando no esta autorizado
        elif mensaje == "Unauthorized":
            response.data = {"CODE_ERR": "UNAUTHORIZED."}
            response.status_code = status.HTTP_403_FORBIDDEN
    return response
