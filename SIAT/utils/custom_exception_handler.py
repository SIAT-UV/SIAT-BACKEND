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

        elif mensaje == "Invalid token.":
            response.data = {"CODE_ERR": "INVALID_TOKEN."}
            response.status_code = status.HTTP_403_FORBIDDEN
        
        elif response.data.get("code") == "token_not_valid":
            for msg in response.data.get("messages", []):
                if msg.get("message") == "Token is expired" and msg.get("token_class") == "AccessToken":
                    response.data = {"CODE_ERR": "ACCESS_TOKEN_EXPIRED."}
                    response.status_code = status.HTTP_403_FORBIDDEN
                    break


        elif mensaje == "Given token not valid for any token type":
            response.data = {"CODE_ERR": "NOT_VALID_TOKEN_TYPE."}
            response.status_code = status.HTTP_401_UNAUTHORIZED
    
        elif mensaje == "Token is blacklisted":
            response.data = {"CODE_ERR": "TOKEN_IS_BLACKLISTED."}
            response.status_code = status.HTTP_401_UNAUTHORIZED


    return response
