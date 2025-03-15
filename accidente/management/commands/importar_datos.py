import requests
from datetime import datetime, time
from django.core.management.base import BaseCommand
from accidente.models import Accidente, Ubicacion

API_URL = "https://www.datos.gov.co/resource/ezt8-5wyj.json"

class Command(BaseCommand):
    help = "Importar datos de accidentes desde la API"

    def handle(self, *args, **kwargs):
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            for item in data:
                fecha = self.parse_date(item.get("fecha", ""))
                if fecha is None:
                    self.stderr.write(self.style.ERROR(f"Fecha inválida en registro: {item}"))
                    continue  # Omitir registro si la fecha es inválida
                
                hora = self.parse_time(item.get("hora", "").strip())
                if hora is None:
                    self.stderr.write(self.style.ERROR(f"Hora inválida en registro: {item}"))
                    continue  # Omitir registro si la hora es inválida

                # Crear o recuperar Ubicacion
                ubicacion, _ = Ubicacion.objects.get_or_create(
                    AREA=item.get("area", ""),
                    DIRECCION_HECHO=item.get("direccion_hecho", ""),
                    BARRIO_HECHO=item.get("barrio_hecho", ""),
                    Cordenada_Geografica=str(item.get("cordenada_geografica_", ""))
                )

                accidente, created = Accidente.objects.update_or_create(
                    AÑO=item.get("a_o", 0),
                    FECHA=fecha,
                    DIA=item.get("dia", ""),
                    HORA=hora,
                    CONTROLES_DE_TRANSITO=item.get("controles_de_transito", ""),
                    CLASE_DE_ACCIDENTE=item.get("clase_de_accidente", ""),
                    CLASE_DE_SERVICIO=item.get("clase_de_servicio", ""),
                    GRAVEDAD_DEL_ACCIDENTE=item.get("gravedad_del_accidente", ""),
                    CLASE_DE_VEHICULO=item.get("clase_de_vehiculo", ""),
                    ubicacion=ubicacion, 
                )

                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Registro agregado: {accidente}"))
        else:
            self.stderr.write(self.style.ERROR("Error al obtener los datos de la API"))

    def parse_date(self, date_str):
        """Convierte una fecha de la API en formato ISO 8601 a un objeto date de Python."""
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f").date()
        except ValueError:
            return None  # Retorna None si la fecha no es válida

    def parse_time(self, time_str):
        """Convierte una hora en formato HH:MM:SS o HH:MM:SS AM/PM a un objeto time de Python."""
        if not time_str or isinstance(time_str, str) and time_str.strip().lower() in ["no informa", ""]:
            return None  # Retorna None si la hora está vacía o es "No informa"

        try:
            return datetime.strptime(time_str.strip(), "%H:%M:%S").time()  # Formato 24 horas
        except ValueError:
            try:
                return datetime.strptime(time_str.strip(), "%I:%M:%S %p").time()  # Formato 12 horas AM/PM
            except ValueError:
                self.stderr.write(self.style.ERROR(f"Formato de hora desconocido: {time_str}"))  # Log para depuración
                return None  # Retorna None si la hora no es válida


