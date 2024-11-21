import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "posting_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 90
        },
        {
            "fieldname": "expense_type",
            "label": _("Expense Type"),
            "fieldtype": "Link",
            "options": "Expense Type",
            "width": 120
        },
        {
            "fieldname": "expense_category",
            "label": _("Category"),
            "fieldtype": "Link",
            "options": "Expense Category",
            "width": 120
        },
        {
            "fieldname": "cost_center",
            "label": _("Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 120
        },
        {
            "fieldname": "project",
            "label": _("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "width": 120
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        }
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    data = frappe.db.sql("""
        SELECT
            posting_date,
            expense_type,
            expense_category,
            cost_center,
            project,
            amount,
            status
        FROM `tabExpense Entry`
        WHERE docstatus = 1 %s
        ORDER BY posting_date DESC
    """ % conditions, filters, as_dict=1)
    
    return data

def get_conditions(filters):
    conditions = []
    
    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")
    if filters.get("expense_type"):
        conditions.append("expense_type = %(expense_type)s")
    if filters.get("expense_category"):
        conditions.append("expense_category = %(expense_category)s")
    if filters.get("cost_center"):
        conditions.append("cost_center = %(cost_center)s")
    if filters.get("project"):
        conditions.append("project = %(project)s")
    
    return " AND " + " AND ".join(conditions) if conditions else ""