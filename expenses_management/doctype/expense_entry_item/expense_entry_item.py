from frappe.model.document import Document
from frappe.utils import flt

class ExpenseEntryItem(Document):
    def validate(self):
        self.calculate_amounts()
        
    def calculate_amounts(self):
        self.amount = flt(self.quantity) * flt(self.rate)
        self.total_amount = flt(self.amount) + flt(self.tax_amount)