from .config import report_xbrl_map
from bs4 import BeautifulSoup
from datetime import datetime

def parseNseXbrl(rawXml:str, report_slug: str) -> tuple[dict, dict]:
    print("Parsing XBRL..")
    xmlSoup = BeautifulSoup(rawXml, "lxml")
    parsed_reports = {}
    context_ids = ['DCYMain', 'DPYMain']
    
    def get_context_dates(context_id: str):
        context_el = xmlSoup.find(f'xbrli:context', {'id': context_id})
        start_date_el = context_el.find(name=f'xbrli:startdate')
        end_date_el = context_el.find(name=f'xbrli:enddate')
        # print(start_date_el.get_text(), end_date_el)

        start_date = datetime.strptime(start_date_el.get_text(), '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_el.get_text(), '%Y-%m-%d').date()
        return start_date, end_date
    
    for name, value in report_xbrl_map.items():
        for ctx_id in context_ids:
            if ctx_id not in parsed_reports:
                parsed_reports[ctx_id] = {}
            
            parsed_reports[ctx_id]["report_slug"] = report_slug
            parsed_reports[ctx_id]["start_date"], parsed_reports[ctx_id]["end_date"] = get_context_dates(ctx_id)
            
            field_el = None
            if 'context_ref' in value:
                field_el = xmlSoup.find(
                    name=f'in-capmkt:{value["verbose_name"].lower()}', 
                    attrs={'contextref': value["context_ref"]}
                )
            else:
                field_el = xmlSoup.find(
                    name=f'in-capmkt:{value["verbose_name"].lower()}', 
                    attrs={'contextref': ctx_id}
                )
            # print("########################", field_el)
            inner_text = -1
            if not field_el:
                inner_text = -1
            else:
                inner_text = field_el.text
            
              
            final_value = None
            if value["data_type"] == "int":
                try:
                    final_value = int(inner_text)
                except ValueError as ie:
                    final_value = -1
            elif value["data_type"] == "float":
                try:
                    final_value = float(inner_text)
                except ValueError as fe:
                    final_value = -1
            else:
                final_value = inner_text
            parsed_reports[ctx_id][name] = final_value

            
    return parsed_reports["DCYMain"], parsed_reports["DPYMain"]
    