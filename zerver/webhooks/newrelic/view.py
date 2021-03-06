# Webhooks for external integrations.
from typing import Any, Dict, Optional

from django.http import HttpRequest, HttpResponse

from zerver.decorator import api_key_only_webhook_view
from zerver.lib.request import REQ, has_request_variables
from zerver.lib.response import json_success
from zerver.lib.webhooks.common import check_send_webhook_message, \
    UnexpectedWebhookEventType
from zerver.lib.validator import check_dict
from zerver.models import UserProfile

@api_key_only_webhook_view("NewRelic")
@has_request_variables
def api_newrelic_webhook(request: HttpRequest, user_profile: UserProfile,
                         alert: Optional[Dict[str, Any]]=REQ(validator=check_dict([]), default=None),
                         deployment: Optional[Dict[str, Any]]=REQ(validator=check_dict([]), default=None)
                         ) -> HttpResponse:
    if alert:
        # Use the message as the subject because it stays the same for
        # "opened", "acknowledged", and "closed" messages that should be
        # grouped.
        subject = alert['message']
        content = "%(long_description)s\n[View alert](%(alert_url)s)" % (alert)
    elif deployment:
        subject = "%s deploy" % (deployment['application_name'])
        content = """`%(revision)s` deployed by **%(deployed_by)s**
%(description)s

%(changelog)s""" % (deployment)
    else:
        raise UnexpectedWebhookEventType('New Relic', 'Unknown Event Type')

    check_send_webhook_message(request, user_profile, subject, content)
    return json_success()
