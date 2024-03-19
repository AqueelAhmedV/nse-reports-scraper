from django.db import models
from emissions_scraper.config import report_xbrl_map
from datetime import datetime

class EmissionReport(models.Model):
    report_slug = models.CharField(max_length=150)
    report_id = models.CharField(max_length=150, unique=True, default='')
    company_name = models.CharField(max_length=200, default='')
    company_symbol = models.CharField(max_length=100, default='')
    start_date = models.DateField(default=datetime.today)
    end_date = models.DateField(default=datetime.today)
    not_found = models.BooleanField(default=False)

    for field_name, field_schema in report_xbrl_map.items():
        if field_schema["data_type"] == "float":
            locals()[field_name] = models.FloatField(
                verbose_name=field_schema["verbose_name"], default=-1.0)
        elif field_schema["data_type"] == "int":
            locals()[field_name] = models.IntegerField(
                verbose_name=field_schema["verbose_name"], default=-1)
        else:
            locals()[field_name] = models.CharField(
                max_length=200, verbose_name=field_schema["verbose_name"], default='')

    @property
    def renewable_electric_usage(self):
        renewable = self.renewable_electric
        total = self.total_electric
        if total == -1 or renewable == -1:
            return -1
        else:
            return renewable/total


    def __str__(self):
        return self.report_id
