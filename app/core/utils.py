from django.utils.deconstruct import deconstructible

@deconstructible
class UploadToPath:
    def __init__(self, tipo_doc):
        self.tipo_doc = tipo_doc

    def __call__(self, instance, filename):
        # Lógica para obtener el identificador (CI)
        if hasattr(instance, 'empleado') and instance.empleado:
            identificador = instance.empleado.ci
        elif hasattr(instance, 'ci'):
            identificador = instance.ci
        else:
            identificador = 'sin_id'

        # Retornamos la ruta
        return f'empleado/{identificador}/DOC/{self.tipo_doc}/{filename}'