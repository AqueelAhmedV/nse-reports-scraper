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


def init_driver():
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

    return webdriver.Chrome(options=chrome_options), chrome_options


def retry_method(func, success: bool, max_retries=5, cleanup=None, *args, **kwargs):
    retry_count = 0
    while retry_count < max_retries and not success:
        try:
            data, cleanup = func(*args, **kwargs)
            success = True
            return data, success
        except RetryableException as e:
            if cleanup:
                cleanup()
            print(f"An error occurred: {str(e)}")
            # Increment retry count
            retry_count += 1
            print(f"Retrying... Attempt {retry_count}/{max_retries}")
    

def fetch_nse_reports():
    try:
        driver, chrome_options = init_driver()
        wait = WebDriverWait(driver, 10)
        driver.get(NSE_SUSTAINABILITY_PAGE)
        wait.until(
            EC.presence_of_element_located((By.TAG_NAME, 'footer'))
        )
        response = driver.execute_script(
            f'return fetch("{NSE_EMISSIONS_REPORT_API}").then(r => r.json())')
        data = response["data"]    
        print(f'{len(data)} records found')
        
        def cleanup():
            driver.quit()
        
        return data, cleanup
    except KeyboardInterrupt:
        raise
    except Exception as e:
        raise RetryableException(e)
    
class XMLFetcher:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.initialized = False

    def init_fetch_xml(self):
        if not self.initialized:
            self.driver, _opts = init_driver()
            self.wait = WebDriverWait(self.driver, 10)
            self.initialized = True

    def fetch_raw_xml(self, link:str):
        self.init_fetch_xml()
        rawXml = None
        try:
            self.driver.get(link)
            self.wait.until(EC.presence_of_element_located((By.ID, 'webkit-xml-viewer-source-xml')))
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            rawXml = soup.find('div', {'id': 'webkit-xml-viewer-source-xml'}).contents[0].__str__()
            print("XML Loaded")
            def cleanup():
                if self.driver:
                    self.driver.quit()
                    self.driver = None
            return rawXml, cleanup
        except TimeoutException as te1:
            try:
                error_el = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'errorContainer')))
                if error_el:
                    EmissionReport.objects.create(
                        report_slug=get_nse_report_slug(link),
                        report_id= get_nse_report_slug(link) + '_404',
                        not_found=True
                    )
                    raise ReportNotFoundException("Report not found")
            except TimeoutException as final_e:
                raise RetryableException("XML load error")
        except ReportNotFoundException:
            raise
        except RetryableException:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as some_other_e:
            raise RetryableException(some_other_e)



def scrape_nse_reports() -> list[str]:#scrape_nse_emissions_reports():
    data_loaded = False

    data, data_loaded = retry_method(
        func=fetch_nse_reports,
        success=data_loaded,
        max_retries=5,
    )

    if not data_loaded:
        return
    
    new_data = [d for d in data if not
                    EmissionReport.objects.filter(
                        report_slug=get_nse_report_slug(d["xbrlFile"])).exists()]
    
    new_data_count = len(new_data)
    print(f'{new_data_count} new reports found')
    
    if new_data_count == 0:
        return
    


    for i,nd in enumerate(new_data): 
        link = nd["xbrlFile"]
        xml_loaded = False
        xml_fetcher = XMLFetcher()
        try:
            rawXml, xml_loaded = retry_method(
                func=xml_fetcher.fetch_raw_xml,
                max_retries=3,
                success=xml_loaded,
                link=link,
            )
        except ReportNotFoundException as nfe:
            print(str(nfe))
            continue

        
        common_fields = {
            "company_name": nd["companyName"],
            "company_symbol": nd["symbol"]
        }
        new_report_dcy, new_report_dpy = parseNseXbrl(
            rawXml=rawXml, 
            report_slug=get_nse_report_slug(link)
        )
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