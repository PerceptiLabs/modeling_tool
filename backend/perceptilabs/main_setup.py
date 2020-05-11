import os

import logging
import sentry_sdk
from sentry_sdk import utils

import perceptilabs.utils as utils
from perceptilabs.analytics.scraper import get_scraper
from perceptilabs.databundle import DataBundle, AzureUploader, AZURE_ACCOUNT_NAME_EU, AZURE_ACCOUNT_KEY_EU, AZURE_CONTAINER_EU, AZURE_ACCOUNT_NAME_US, AZURE_ACCOUNT_KEY_US, AZURE_CONTAINER_US

log = logging.getLogger(__name__)
scraper = get_scraper()

def setup_sentry(user=None, commit_id=None):
    def strip_unimportant_errors(event, hint):
        log_ignores=['Error in getTestingStatistics', 'Error in getTrainingStatistics', ]

        if 'log_record' in hint:
            if hint['log_record'].msg in log_ignores:
                return None

        if 'exc_info' in hint:
            from core_new.history import HistoryInputException
            exc_type, exc_value, tb = hint['exc_info']
            if isinstance(exc_value, HistoryInputException):
                return None
                
        return event

    sentry_sdk.init("https://9b884d2181284443b90c21db68add4d7@sentry.io/1512385", before_send=strip_unimportant_errors, release=str(commit_id))

    with sentry_sdk.configure_scope() as scope:
        scope.set_tag('error-type', 'internal-error')
        sentry_sdk.utils.MAX_STRING_LENGTH = 5000

        if user:
            scope.user = {"email" : user}
        


def setup_scraper():
    data_uploaders = [
        AzureUploader(AZURE_ACCOUNT_NAME_EU, AZURE_ACCOUNT_KEY_EU, AZURE_CONTAINER_EU),
        AzureUploader(AZURE_ACCOUNT_NAME_US, AZURE_ACCOUNT_KEY_US, AZURE_CONTAINER_US)        
    ]                               
    data_bundle = DataBundle(data_uploaders)
    utils.dump_system_info(os.path.join(data_bundle.path, 'system_info.json'))
    utils.dump_build_info(os.path.join(data_bundle.path, 'build_info.json'))    

    scraper.start()
    scraper.set_output_directory(data_bundle.path)

    return data_bundle
