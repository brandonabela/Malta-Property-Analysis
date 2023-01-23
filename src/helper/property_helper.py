import re

from selenium.webdriver.chrome.webdriver import WebDriver

from helper.configuration import Configuration
from helper.dynamic_scrape import DynamicScrape


class PropertyHelper(object):
    plan_re = re.compile('|'.join(Configuration.stage_plan()), re.IGNORECASE)
    shell_re = re.compile('|'.join(Configuration.stage_shell()), re.IGNORECASE)
    finished_re = re.compile('|'.join(Configuration.stage_finished()), re.IGNORECASE)
    furnished_re = re.compile('|'.join(Configuration.stage_furnished()), re.IGNORECASE)
    unconverted_re = re.compile('|'.join(Configuration.stage_unconverted()), re.IGNORECASE)

    def determine_stage(driver: WebDriver, x_description: str, is_sale: bool) -> str:
        if is_sale:
            description = DynamicScrape.get_text(driver, x_description).lower()

            if PropertyHelper.plan_re.search(description):
                return 'Plan'
            elif PropertyHelper.shell_re.search(description):
                return 'Shell'
            elif PropertyHelper.finished_re.search(description):
                return 'Finished'
            elif PropertyHelper.furnished_re.search(description):
                return 'Furnished'
            elif PropertyHelper.unconverted_re.search(description):
                return 'Unconverted'
            else:
                return 'Unclassified'
        else:
            return 'Furnished'
