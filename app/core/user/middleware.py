from django.shortcuts import redirect
from django.urls import reverse

class EnforcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Solo actuar si el usuario está logueado
        if request.user.is_authenticated:
            # 2. Revisar tu campo is_change_password
            if request.user.is_change_password:
                # Definir rutas permitidas para que no haya un bucle infinito
                url_cambio = reverse('force_password_change') # Asegúrate que este name exista en urls.py
                url_logout = reverse('logout')
                
                # 3. Si no está en una URL permitida, redirigir
                if request.path not in [url_cambio, url_logout] and not request.path.startswith('/static/'):
                    return redirect(url_cambio)

        response = self.get_response(request)
        return response