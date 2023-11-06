from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from otree.models import Session, Participant
from django.shortcuts import redirect, reverse
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
import json
from .models import Message
import logging
from django.utils import timezone
from pprint import pprint

RETURNED_STATUSES = ["RETURNED", "TIMED-OUT", "REJECTED"]
STATUS_CHANGE = "submission.status.change"
logger = logging.getLogger("benzapp.views")


class PandasExport(View):
    url_name = None

    def get(self, request, *args, **kwargs):
        params = dict()
        df = self.get_data(params)
        if df is not None and not df.empty:
            timestamp = timezone.now()
            curtime = timestamp.strftime("%m_%d_%Y_%H_%M_%S")
            csv_data = df.to_csv(index=False)
            response = HttpResponse(csv_data, content_type=self.content_type)
            filename = f"{self.url_name}_{curtime}.csv"
            response["Content-Disposition"] = f"attachment; filename={filename}"
            return response
        else:
            return redirect(reverse("ExportIndex"))


class MessageDataExport(PandasExport):
    display_name = "Message Data export"
    url_name = "message_data_export"
    url_pattern = rf"message_data_export"
    content_type = "text/csv"

    def get_data(self, params):
        fields = ("owner__participant__code",
                  "owner__round_number",
                  "owner__session__code",
                  "utc_time",
                  "message",

                  )
        messages = Message.objects.all().values(*fields)
        if not messages.exists():
            return
        if messages.exists():
            df = pd.DataFrame(data=messages)

            return df
