app_name = "expenses_management"
app_title = "Expenses Management"
app_publisher = "Your Company"
app_description = "Comprehensive Expense Management System"
app_email = "your.email@example.com"
app_license = "MIT"

# Document Events
doc_events = {
    "Expense Entry": {
        "on_submit": "expenses_management.expenses_management.doctype.expense_entry.expense_entry.on_submit",
        "on_cancel": "expenses_management.expenses_management.doctype.expense_entry.expense_entry.on_cancel"
    }
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "expenses_management.expenses_management.doctype.expense_entry.expense_entry.send_expense_reminders"
    ]
}

# Custom Roles
has_permission = {
    "Expense Entry": "expenses_management.expenses_management.doctype.expense_entry.expense_entry.has_permission"
}