import requests
from celery import shared_task, states
from celery.utils.log import get_task_logger
from decouple import config
from django.utils import timezone

from income.models import Hiring, HiringStatusChoices

logger = get_task_logger(__name__)

GRAPH_API_URL = "https://graph.facebook.com/v16.0/"
FROM_PHONE_NUMBER_ID = config("FROM_PHONE_NUMBER_ID")
ACCESS_TOKEN = config("ACCESS_TOKEN")


def send_whatsapp_acceptance(phone_number):
    messages_url = f"{GRAPH_API_URL}{FROM_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": f"54{phone_number}",
        "type": "template",
        "text": {"name": "hello_world", "language": {"code": "en_US"}},
        # "text": {"name": "acceptance", "language": {"code": "es_AR"}},
    }
    requests.post(messages_url, headers=headers, json=data)


def send_whatsapp_message(phone_number, message):
    messages_url = f"{GRAPH_API_URL}{FROM_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": f"54{phone_number}",
        "type": "text",
        "text": {"body": message},
    }
    requests.post(messages_url, headers=headers, json=data)


def set_message_as_read(message_id):
    messages_url = f"{GRAPH_API_URL}/messages/{message_id}"
    data = {
        "status": "read",
    }
    requests.put(messages_url, params=data)


def handle_webhook(data):
    # contact_id = data["entry"][0]["changes"]["value"]["contacts"][0]["wa_id"]
    message_id = data["entry"][0]["changes"]["value"]["messages"][0]["id"]
    # message_text = data["entry"][0]["changes"]["value"]["messages"][0]["text"][
    #     "body"
    # ]
    set_message_as_read(message_id)


@shared_task(bind=True)
def update_hiring_status(self):
    today = timezone.now().date
    ongoing_hiring_qs = Hiring.objects.filter(status=HiringStatusChoices.ONGOING)

    outdated_hiring_list = []

    for hiring in ongoing_hiring_qs:
        if hiring.tasks.filter(
            service__service_type_id__in=[3, 4], start_date__lt=today, is_done=False
        ).exists():
            hiring.status = HiringStatusChoices.CLEANING_PENDING
            outdated_hiring_list.append(hiring)

    outdated_hiring_amount = Hiring.objects.bulk_update(
        outdated_hiring_list, ["status"]
    )

    if outdated_hiring_amount:
        self.update_state(
            state=states.SUCCESS,
            meta=f"Successfully updated {outdated_hiring_amount} hiring status.",
        )
        logger.info(f"Successfully updated {outdated_hiring_amount} hiring status.")
    else:
        self.update_state(
            state=states.SUCCESS,
            meta="No hiring to update its status were found.",
        )
        logger.info("No hiring to update its status were found.")


# def send_whatsapp_media(phone_number, message):
#     messages_url = f"{GRAPH_API_URL}{FROM_PHONE_NUMBER_ID}/messages"
#     headers = {
#         "Authorization": f"Bearer {ACCESS_TOKEN}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "messaging_product": "whatsapp",
#         "recipient_type": "individual",
#         "to": f"54{phone_number}",
#         "type": "text",
#         "text": {"body": message},
#     }
#     response = requests.post(messages_url, headers=headers, json=data)
