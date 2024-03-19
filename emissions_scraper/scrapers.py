from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import OperatingSystem, SoftwareName

from .parsers import parseNseXbrl
from emissions_app.helpers import generate_nse_report_id, get_nse_report_slug
from emissions_app.models import EmissionReport

from .config import NSE_EMISSIONS_REPORT_API,NSE_SUSTAINABILITY_PAGE
from .exceptions import ReportNotFoundException, RetryableException

from typing import Callable, Tuple


class Fetcher:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.initialized = False
        self._max_retries = 3

    @property
    def max_retries(self):
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value):
        self._max_retries = value

    def init_driver(self):
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
        user_agent_rotator = UserAgent(software_names=software_names,
                                        operating_systems=operating_systems,
                                        limit=100)
        user_agent = user_agent_rotator.get_random_user_agent()

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'--user-agent={user_agent}')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.initialized = True

    def fetch(self):
        NotImplementedError("subclass should define fetch method")

    def fetch_with_retry(self, *args, **kwargs):
        return self.retry(self.fetch, *args, **kwargs)

    def cleanup(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def retry(self, func: Callable, *args, **kwargs):
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                return func(*args, **kwargs)
            except RetryableException as e:
                print(f"An error occurred: {str(e)}")
                retry_count += 1
                self.cleanup()
                if hasattr(func, 'is_retry') and func.is_retry:
                    kwargs['is_retry'] = True
                print(f"Retrying... Attempt {retry_count}/{self.max_retries}")
        raise RetryableException("Max retries reached.")

class NSEFetcher(Fetcher):
    max_retries = 5
    def fetch(self) -> Tuple[list, bool]:
        self.init_driver()
        data = None
        data_loaded = False
        try:
            self.driver.get(NSE_SUSTAINABILITY_PAGE)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'footer')))
            response = self.driver.execute_script(f'return fetch("{NSE_EMISSIONS_REPORT_API}").then(r => r.json())')
            data = response["data"]    
            data_loaded = True
            print(f'{len(data)} records found')
        except TimeoutException as e:
            print(f"TimeoutException: {e}")
            raise RetryableException("Failed to fetch NSE reports.")
        except Exception as e:
            print(f"Exception occurred: {e}")
            raise RetryableException("Failed to fetch NSE reports.")
        
        self.driver.quit()
        return data, data_loaded

class XMLFetcher(Fetcher):
    def fetch(self, link:str, is_retry=False) -> Tuple[str, bool]:
        if is_retry or not self.driver:
            self.init_driver()
        rawXml = None
        xml_loaded = False
        try:
            self.driver.get(link)
            self.wait.until(EC.presence_of_element_located((By.ID, 'webkit-xml-viewer-source-xml')))
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            rawXml = soup.find('div', {'id': 'webkit-xml-viewer-source-xml'}).contents[0].__str__()
            print("XML Loaded")
            xml_loaded = True
        except TimeoutException as te1:
            try:
                error_el = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'errorContainer')))
                if error_el:
                    EmissionReport.objects.create(
                        report_slug=get_nse_report_slug(link),
                        report_id= get_nse_report_slug(link) + '_404',
                        not_found=True
                    )
                    raise ReportNotFoundException("Report not found")  # This line raises ReportNotFoundException
            except TimeoutException as final_e:
                raise RetryableException("XML load error")
        except ReportNotFoundException:  # This block does nothing but re-raise the exception
            raise
        except RetryableException:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as some_other_e:
            raise RetryableException(some_other_e)
        return rawXml, xml_loaded

class NSEReportScraper:
    def __init__(self):
        self.nse_fetcher = NSEFetcher()
        self.xml_fetcher = XMLFetcher()

    def scrape_nse_reports(self):
        try:
            data, data_loaded = self.nse_fetcher.fetch_with_retry()
            if not data_loaded:
                return
            new_data = [d for d in data if not EmissionReport.objects.filter(report_slug=get_nse_report_slug(d["xbrlFile"])).exists()]
            new_data_count = len(new_data)
            print(f'{new_data_count} new reports found')
            if new_data_count == 0:
                return

            for i, nd in enumerate(new_data): 
                link = nd["xbrlFile"]
                xml_loaded = False
                try:
                    rawXml, xml_loaded = self.xml_fetcher.fetch_with_retry(link)
                except ReportNotFoundException as nfe:
                    print(str(nfe))
                    continue
                common_fields = {
                    "company_name": nd["companyName"],
                    "company_symbol": nd["symbol"]
                }
                new_report_dcy, new_report_dpy = parseNseXbrl(rawXml=rawXml, report_slug=get_nse_report_slug(link))
                print("Parsed")
                new_db_entries = [
                    EmissionReport(
                        report_id=generate_nse_report_id(new_report_dcy),
                        **common_fields,
                        **new_report_dcy
                    ),
                    EmissionReport(
                        report_id=generate_nse_report_id(new_report_dpy),
                        **common_fields,
                        **new_report_dpy
                    )
                ]
                EmissionReport.objects.bulk_create(new_db_entries)
                print(f'Added {i+1} of {new_data_count}')
            print("NSE Reports Sync Complete")
        except RetryableException as e:
            print(f"RetryableException occurred: {e}")

