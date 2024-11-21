from frappe.model.document import Document

class ExpenseType(Document):
    def validate(self):
        self.validate_account()
    
    def validate_account(self):
        from erpnext.accounts.doctype.account.account import get_account_type
        account_type = get_account_type(self.account)
        if account_type not in ['Expense Account', 'Cost of Goods Sold']:
            frappe.throw(_("Account must be an Expense Account or Cost of Goods Sold Account"))