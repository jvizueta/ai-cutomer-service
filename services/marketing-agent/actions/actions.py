import os
import logging
import pytz
from datetime import datetime, timedelta
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

logger = logging.getLogger(__name__)

TIMEZONE = pytz.timezone("America/Bogota")

class ActionSetServicio(Action):
    def name(self) -> Text:
        return "action_set_servicio"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        # Extract intent to infer service
        intent = tracker.latest_message.get("intent", {}).get("name")
        servicio_map = {
            "servicio_social_media": "Social Media",
            "servicio_google_ads": "Google Ads",
            "servicio_diseno_web": "Diseño Web",
            "servicio_diseno_grafico": "Diseño Gráfico",
            "servicio_publicidad_exterior": "Publicidad Exterior"
        }
        servicio = servicio_map.get(intent)
        if servicio:
            logger.info(f"Servicio identificado: {servicio}")
            dispatcher.utter_message(text=f"Excelente, trabajemos en {servicio}. Para orientarte mejor necesito hacerte unas preguntas.")
            return [SlotSet("servicio_interes", servicio)]
        return []

class ActionProporcionarValor(Action):
    def name(self) -> Text:
        return "action_proporcionar_valor"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        servicio = tracker.get_slot("servicio_interes")
        valor_map = {
            "Social Media": "Nuestro servicio mensual incluye estrategia, planificación, diseño, redacción, gestión de pauta y reporte completo.",
            "Google Ads": "Analizamos tu web, configuramos Analytics, Tag Manager y seguimiento de conversiones.",
            "Diseño Web": "Creamos sitios rápidos, adaptables y optimizados para SEO en WordPress o Prestashop.",
            "Diseño Gráfico": "Diseñamos desde logotipos y manuales hasta piezas para campañas y contenido audiovisual.",
            "Publicidad Exterior": "Gestionamos vallas, buses, taxis, mupis y activaciones de marca en zonas estratégicas."
        }
        if servicio in valor_map:
            dispatcher.utter_message(text=valor_map[servicio])
        else:
            dispatcher.utter_message(text="Nuestros servicios cubren social media, diseño web, publicidad exterior, diseño gráfico y Google Ads.")
        return []

class ActionAgendarReunion(Action):
    def name(self) -> Text:
        return "action_agendar_reunion"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        # Extract provided date text
        fecha_texto = tracker.latest_message.get("text")
        fecha_slot = None
        hora_slot = None
        now = datetime.now(TIMEZONE)
        logger.info(f"Intentando parsear fecha de entrada: {fecha_texto}")
        
        # Very naive parsing
        if "mañana" in fecha_texto.lower():
            fecha_slot = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "lunes" in fecha_texto.lower():
            # Find next Monday
            days_ahead = (0 - now.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7
            fecha_slot = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        elif any(dia in fecha_texto.lower() for dia in ["martes","miércoles","jueves","viernes","sábado","domingo"]):
            # Simplify: set +3 days
            fecha_slot = (now + timedelta(days=3)).strftime("%Y-%m-%d")
        else:
            # Try direct date pattern (e.g., 20 de octubre) - skipped for brevity
            fecha_slot = (now + timedelta(days=2)).strftime("%Y-%m-%d")

        hora_slot = "15:00"  # default placeholder
        dispatcher.utter_message(text=f"Agendado tentativamente para {fecha_slot} a las {hora_slot}. Confirmaremos disponibilidad.")
        return [SlotSet("fecha_reunion", fecha_slot), SlotSet("hora_reunion", hora_slot)]

class ActionCheckAvailabilityCalendar(Action):
    def name(self) -> Text:
        return "action_check_availability_calendar"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        fecha = tracker.get_slot("fecha_reunion")
        hora = tracker.get_slot("hora_reunion")
        if not fecha:
            dispatcher.utter_message(text="Necesito una fecha para revisar disponibilidad. ¿Qué día te vendría bien?")
            return []
        # Stub: Always available
        dispatcher.utter_message(text=f"Confirmado, el {fecha} a las {hora} está disponible. Un estratega te contactará.")
        return []

class ActionHandlePrecios(Action):
    def name(self) -> Text:
        return "action_handle_precios"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        dispatcher.utter_message(text="Los costos dependen del alcance y objetivos. Lo ideal es una reunión diagnóstica para darte una propuesta precisa.")
        dispatcher.utter_message(text="¿Te gustaría que agendemos esa reunión?")
        return []

class ActionFallback(Action):
    def name(self) -> Text:
        return "action_fallback"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        dispatcher.utter_message(text="No estoy seguro de haber entendido. ¿Puedes indicarme el servicio que te interesa o reformular?")
        return []

class ActionLoadBrandContext(Action):
    def name(self) -> Text:
        return "action_load_brand_context"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        company = os.getenv("COMPANY_NAME")
        nickname = os.getenv("AGENT_NICKNAME")
        # Only set if not already present to avoid overwriting in-session adjustments
        events = []
        if not tracker.get_slot("company_name"):
            events.append(SlotSet("company_name", company))
        if not tracker.get_slot("agent_nickname"):
            events.append(SlotSet("agent_nickname", nickname))
        logging.getLogger(__name__).info(f"Loaded brand context company={company} agent={nickname}")
        return events
