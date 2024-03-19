from django.core.management.base import BaseCommand
from emissions_scraper.scrapers import NSEReportScraper
from emissions_app.models import EmissionReport

class Command(BaseCommand):
    help = 'Scrape and parse emission reports'

    def handle(self, *args, **options):
        # Scrape reports from the website
        try:
            nse_scraper = NSEReportScraper()
            nse_scraper.scrape_nse_reports()
            # self.stdout.write(self.style.SUCCESS("NSE Emission Reports Updated"))
        except KeyboardInterrupt:
            print("Operation aborted")
        except Exception as e:
            self.stdout.write(self.style.ERROR("scrape_reports ERROR: " + str(e)))

        