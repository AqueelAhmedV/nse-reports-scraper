
NSE_EMISSIONS_REPORT_API = "https://www.nseindia.com/api/corporate-bussiness-sustainabilitiy?"
NSE_SUSTAINABILITY_PAGE = "https://www.nseindia.com/companies-listing/corporate-filings-bussiness-sustainabilitiy-reports"

report_xbrl_map =  {
    'scope_1_emissions': {
        'data_type': 'float', 
        'verbose_name': 'TotalScope1Emissions'
    },
    'scope_2_emissions': {
        'data_type': 'float', 
        'verbose_name': 'TotalScope2Emissions'
    },
    'both_emissions_turnover': {
        'data_type': 'float', 
        'verbose_name': 'TotalScope1AndScope2EmissionsPerRupeeOfTurnover'
    },
    'both_emission_intensity': {
        'data_type': 'float', 
        'verbose_name': 'TotalScope1AndScope2EmissionIntensity'
    },
    'scope_3_emissions': {
        'data_type': 'float', 
        'verbose_name': 'TotalScope3Emissions'
    },
    'scope_3_emission_intensity': {
        'data_type': 'float', 
        'verbose_name': 'TotalScope3EmissionIntensity'
    },
    'scope_3_emissions_turnover': {
        'data_type': 'float', 
        'verbose_name': 'TotalScope3EmissionsPerRupeeOfTurnover'
    },
    'nox': {
        'data_type': 'str', 
        'verbose_name': 'Nox'
    },
    'sox': {
        'data_type': 'str',
        'verbose_name': 'Sox',
    },
    'nic_code_entity': {
        'data_type': 'float', 
        'verbose_name': 'NICCodeOfProductOrServiceSoldByTheEntity',
        'context_ref': 'D_ProductServiceSold1'
    },
    'nic_code_lifecycle_1': {
        'data_type': 'float', 
        'verbose_name': 'NICCodeOfProductOrServiceOfConductedLifecyclePerspective',
        'context_ref': 'D_TheEntityConductedLifeCyclePerspectiveOrAssessments1' 
    },
    'nic_code_lifecycle_2': {
        'data_type': 'float', 
        'verbose_name': 'NICCodeOfProductOrServiceOfConductedLifecyclePerspective',
        'context_ref': 'D_TheEntityConductedLifeCyclePerspectiveOrAssessments2' 
    },
    'nic_code_lifecycle_3': {
        'data_type': 'float', 
        'verbose_name': 'NICCodeOfProductOrServiceOfConductedLifecyclePerspective',
        'context_ref': 'D_TheEntityConductedLifeCyclePerspectiveOrAssessments3' 
    },
    'total_electric': {
        'data_type': 'float',
        'verbose_name': 'TotalElectricityConsumption'
    },
    'renewable_electric': {
        'data_type': 'float',
        'verbose_name': 'TotalElectricityConsumptionFromRenewableSources'
    },
    'company_website': {
        'data_type': 'str',
        'verbose_name': 'WebsiteOfCompany',
        'context_ref': 'DCYMain'
    },
    'turnover': {
        'data_type': 'float',
        'verbose_name': 'Turnover',
        'context_ref': 'DCYMain'
    }
}

