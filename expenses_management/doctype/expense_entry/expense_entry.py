import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, flt

class ExpenseEntry(Document):
    def validate(self):
        self.validate_amounts()
        self.validate_duplicate_entries()
        self.validate_user_permissions()
        
    def before_save(self):
        if not self.expense_id:
            self.expense_id = self.generate_expense_id()
            
    def on_submit(self):
        self.create_gl_entries()
        
    def validate_amounts(self):
        if flt(self.amount) <= 0:
            frappe.throw(_("Amount must be greater than zero"))
            
        total_item_amount = sum(flt(item.amount) for item in self.items)
        if flt(self.amount) != total_item_amount:
            frappe.throw(_("Total amount does not match with sum of item amounts"))
            
    def validate_duplicate_entries(self):
        filters = {
            "posting_date": self.posting_date,
            "expense_type": self.expense_type,
            "amount": self.amount,
            "supplier": self.supplier,
            "name": ["!=", self.name]
        }
        
        duplicate = frappe.db.exists("Expense Entry", filters)
        if duplicate:
            frappe.throw(_("Duplicate expense entry found: {0}").format(duplicate))
            
    def validate_user_permissions(self):
        user = frappe.session.user
        roles = frappe.get_roles(user)
        
        if "System Manager" in roles:
            return
            
        if self.workflow_state == "Draft" and not any(role in roles for role in ["Expense User", "Expense Manager"]):
            frappe.throw(_("Only Expense Users and Managers can create draft entries"))
            
        if self.workflow_state == "Pending Approval" and not any(role in roles for role in ["Expense Approver", "Expense Manager"]):
            frappe.throw(_("Only Expense Approvers and Managers can process pending entries"))
            
        if self.workflow_state in ["Approved", "Rejected"] and "Expense Manager" not in roles:
            frappe.throw(_("Only Expense Managers can modify approved or rejected entries"))
            
    def generate_expense_id(self):
        # Generate a unique expense ID based on naming series
        return frappe.get_doc("Naming Series").get_current_value("EXP-")
        
    def create_gl_entries(self):
        from erpnext.accounts.general_ledger import make_gl_entries
        
        gl_entries = []
        
        # Debit expense account
        gl_entries.append({
            "account": self.account_code,
            "debit": self.amount,
            "credit": 0,
            "against": self.supplier,
            "cost_center": self.cost_center,
            "project": self.project,
            "posting_date": self.posting_date,
            "remarks": self.description
        })
        
        # Credit supplier/payable account
        gl_entries.append({
            "account": frappe.get_cached_value("Supplier", self.supplier, "default_payable_account"),
            "debit": 0,
            "credit": self.amount,
            "against": self.account_code,
            "party_type": "Supplier",
            "party": self.supplier,
            "cost_center": self.cost_center,
            "project": self.project,
            "posting_date": self.posting_date,
            "remarks": self.description
        })
        
        make_gl_entries(gl_entries, cancel=(self.docstatus == 2))

def has_permission(doc, user=None, permission_type=None):
    if not user:
        user = frappe.session.user
    
    if user == "Administrator":
        return True
        
    roles = frappe.get_roles(user)
    
    if "System Manager" in roles:
        return True
        
    if "Expense Manager" in roles:
        return True
        
    if permission_type == "create" and "Expense User" in roles:
        return True
        
    if permission_type in ["write", "submit"] and doc.owner == user:
        return True
        
    if "Expense Approver" in roles and doc.workflow_state == "Pending Approval":
        return True
        
    return False

@frappe.whitelist()
def submit_expense(docname):
    doc = frappe.get_doc("Expense Entry", docname)
    if not has_permission(doc, permission_type="submit"):
        frappe.throw(_("Not permitted to submit expense entry"))
    doc.workflow_state = "Pending Approval"
    doc.save()
    return True

@frappe.whitelist()
def approve_expense(docname):
    doc = frappe.get_doc("Expense Entry", docname)
    if not has_permission(doc, permission_type="write"):
        frappe.throw(_("Not permitted to approve expense entry"))
    doc.workflow_state = "Approved"
    doc.approved_by = frappe.session.user
    doc.approval_date = now_datetime()
    doc.submit()
    return True

@frappe.whitelist()
def reject_expense(docname, reason):
    doc = frappe.get_doc("Expense Entry", docname)
    if not has_permission(doc, permission_type="write"):
        frappe.throw(_("Not permitted to reject expense entry"))
    doc.workflow_state = "Rejected"
    doc.add_comment('Comment', text=_("Rejected: {0}").format(reason))
    doc.save()
    return True

@frappe.whitelist()
def return_expense(docname, reason):
    doc = frappe.get_doc("Expense Entry", docname)
    if not has_permission(doc, permission_type="write"):
        frappe.throw(_("Not permitted to return expense entry"))
    doc.workflow_state = "Draft"
    doc.add_comment('Comment', text=_("Returned for revision: {0}").format(reason))
    doc.save()
    return True