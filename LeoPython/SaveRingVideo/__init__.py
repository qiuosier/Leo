import json
import logging
import azure.functions as func

from commons import ring_to_onedrive


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('SaveRingVideo function processed a request.')
    results = ring_to_onedrive.save_to_onedrive()
    return func.HttpResponse(
        json.dumps(dict(processed=results)),
        status_code=200,
        mimetype="application/json"
    )
