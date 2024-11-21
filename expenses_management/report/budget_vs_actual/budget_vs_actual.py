import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "expense_category",
            "label": _("Category"),
            "fieldtype": "Link",
            "options": "Expense Category",
            "width": 150
        },
        {
            "fieldname": "budget_amount",
            "label": _("Budget"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "actual_amount",
            "label": _("Actual"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "variance",
            "label": _("Variance"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "variance_percentage",
            "label": _("Variance %"),
            "fieldtype": "Percent",
            "width": 100
        }
    ]

def get_data(filters):
    fiscal_year = filters.get('fiscal_year')
    if not fiscal_year:
        frappe.throw(_("Please select Fiscal Year"))
    
    # Get budget data
    budget_data = frappe.db.sql("""
        SELECT 
            category_name as expense_category,
            budget_allocation as budget_amount
        FROM `tabExpense Category`
        WHERE fiscal_year = %s
    """, fiscal_year, as_dict=1)
    
    # Get actual expense data
    actual_data = frappe.db.sql("""
        SELECT 
            expense_category,
            SUM(amount) as actual_amount
        FROM `tabExpense Entry`
        WHERE docstatus = 1
        AND YEAR(posting_date) = %s
        GROUP BY expense_category
    """, fiscal_year, as_dict=1)
    
    # Combine and calculate variance
    result = []
    for budget in budget_data:
        row = {
            "expense_category": budget.expense_category,
            "budget_amount": budget.budget_amount,
            "actual_amount": 0,
            "variance": 0,
            "variance_percentage": 0
        }
        
        # Find matching actual data
        for actual in actual_data:
            if actual.expense_category == budget.expense_category:
                row["actual_amount"] = actual.actual_amount
                row["variance"] = budget.budget_amount - actual.actual_amount
                if budget.budget_amount:
                    row["variance_percentage"] = (row["variance"] / budget.budget_amount) * 100
                break
        
        result.append(row)
    
    return result