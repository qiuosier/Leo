import datetime
import logging

import azure.functions as func
from commons import ring_to_onedrive


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logging.info('SaveRingVideoToOnedrive function ran at %s', utc_timestamp)
    if mytimer.past_due:
        logging.info('The timer is past due!')

    results = ring_to_onedrive.save_to_onedrive()
    logging.info("%s events processed.", len(results))
    for result in results:
        logging.info(
            "ID=%s, Created At %s, %s",
            result.get("id"),
            result.get("created_at"),
            result.get("status")
        )

