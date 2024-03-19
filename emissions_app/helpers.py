
def get_nse_report_slug(report_link: str) -> str:
    return report_link.split('/')[5].split('.')[0]

def generate_nse_report_id(report: dict) -> str:
    # print("Generating id")
    return report["report_slug"] + report["start_date"].strftime("%d%m%Y") + report["end_date"].strftime("%d%m%Y")

def get_report_link(report_slug: str) -> str:
    return f'https://nsearchives.nseindia.com/corporate/xbrl/{report_slug}.xml'