from django.db import models
from django.forms import CharField

class Calculation(models.Model):
    service_node_modem = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Обслуживание узла учета с автоматической передачей данных")
    service_node_no_modem = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Обслуживание узла учета без автоматической передачи данных")
    service_four_year_node = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Обслуживание узла учета до 4-х лет")
    automation_node = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Обслуживание узла автоматики")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
       
    def __str__(self):
        return f"Calculation {self.id} - {self.date_created}"
    
    class Meta:
        ordering = ['-date_created']
    
class Subscriber(models.Model):    
    i_number = models.IntegerField(verbose_name="Номер договора", )
    name = models.CharField(max_length=255, verbose_name="Наименование")
    fio = models.CharField(max_length=255, verbose_name="ФИО руководителя")
    post = models.CharField(max_length=255, verbose_name="Должность руководителя")
    short_name = models.CharField(max_length=100, verbose_name="Сокращенное наименование")    
    post_index = models.CharField(max_length=6, verbose_name="Почтовый индекс")
    street = models.CharField(max_length=100, verbose_name="Улица")
    house = models.CharField(max_length=6, verbose_name="Номер дома")
    inn = models.CharField(max_length=12, verbose_name="ИНН")
    account_number = models.CharField(max_length=20, verbose_name="Расчетный счет")
    corr_account = models.CharField(max_length=20, verbose_name="Корр счет")
    bik = models.CharField(max_length=9, verbose_name="БИК")
    kpp = models.CharField(max_length=9, verbose_name="КПП")
    ogrn = models.CharField(max_length=13, verbose_name="ОГРН")
    l_number = models.CharField(max_length=11, verbose_name="Лицевой счет")
    bank_name = models.CharField(max_length=255, verbose_name="Наименование банка")
    hws_node_modem = models.IntegerField(verbose_name="Количество узлов учета ГВС/общих с автоматической передачей данных", default = 0)    
    hws_node_modem_discount = models.IntegerField(verbose_name="Количество узлов ГВС/общих с автоматической передачей данных со скодкой", default = 0)
    hws_node_no_modem = models.IntegerField(verbose_name="Количество узлов учета ГВС/общих без автоматической передачи данных", default = 0)
    hws_node_no_modem_discount = models.IntegerField(verbose_name="Количество узлов ГВС/общих без автоматической передачи данных со скидкой", default = 0)
    heating_node_modem = models.IntegerField(verbose_name="Количество узлов учета отопления с автоматической передачей данных", default = 0)
    heating_node_modem_discount = models.IntegerField(verbose_name = "Количество узлов отопления с автоматической передачей данных со скидкой", default = 0)
    heating_node_no_modem = models.IntegerField(verbose_name="Количество узлов учета отопления без автоматической передачи данных", default = 0)
    heating_node_no_modem_discount = models.IntegerField(verbose_name = "Количество узлов отопления без автоматической передачи данных со скидкой", default = 0)
    hws_automation_node = models.IntegerField(verbose_name="Количество узлов автоматики ГВС", default = 0)
    hws_automation_node_discount = models.IntegerField(verbose_name = "Количество узлов автоматики ГВС со скидкой", default = 0)
    heating_automation_node = models.IntegerField(verbose_name="Количество узлов автоматики отопления", default = 0)
    heating_automation_node_discount = models.IntegerField(verbose_name = "Количество автоматики отопления со скидкой", default = 0)
    hws_four_year_node = models.IntegerField(verbose_name="Количество узлов ГВС/общих до 4-х лет", default=0)
    heating_four_year_node = models.IntegerField(verbose_name="Количество узлов отопления до 4-х лет", default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма договора", default=0.00)
    total_contract_sum = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма всех договоров", default=0.00)
    total_contracts = models.IntegerField(default=0)

    def __str__(self):
        return self.name