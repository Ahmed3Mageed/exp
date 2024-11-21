from frappe.utils.nestedset import NestedSet

class ExpenseCategory(NestedSet):
    def validate(self):
        self.validate_parent()
    
    def validate_parent(self):
        if self.parent_category:
            if self.parent_category == self.name:
                frappe.throw(_("Parent category cannot be same as current category"))