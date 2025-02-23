from django import forms
from .models import Calculation
from .models import Subscriber

class CalculationForm(forms.ModelForm):
    class Meta:
        model = Calculation
        fields = ['service_node_modem', 'service_node_no_modem', 'service_four_year_node', 'automation_node']
        
class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['i_number', 'name', 'short_name', 'post_index', 'street', 'house', 'fio', 'post', 'inn', 
                  'account_number', 'corr_account', 'bik', 'bik', 'kpp', 'ogrn', 'l_number', 
                  'bank_name', 'hws_node_modem', 'hws_node_modem_discount', 'hws_node_no_modem', 'hws_node_no_modem_discount', 'hws_four_year_node', 
                  'heating_node_modem', 'heating_node_modem_discount', 'heating_node_no_modem', 'heating_node_no_modem_discount', 'heating_four_year_node', 
                  'hws_automation_node', 'hws_automation_node_discount', 'heating_automation_node', 'heating_automation_node_discount']

class ContractForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['hws_node_modem', 'hws_node_modem_discount', 'hws_node_no_modem', 'hws_node_no_modem_discount', 'hws_four_year_node', 
                  'heating_node_modem', 'heating_node_modem_discount', 'heating_node_no_modem', 'heating_node_no_modem_discount', 'heating_four_year_node', 
                  'hws_automation_node', 'hws_automation_node_discount', 'heating_automation_node', 'heating_automation_node_discount']