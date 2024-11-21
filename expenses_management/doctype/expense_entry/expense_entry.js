frappe.ui.form.on('Expense Entry', {
    refresh: function(frm) {
        // Add custom buttons based on workflow state
        if (frm.doc.workflow_state === 'Draft') {
            frm.add_custom_button(__('Submit'), function() {
                frm.trigger('submit_expense');
            });
        }
        
        if (frm.doc.workflow_state === 'Pending Approval' && frappe.user.has_role('Expense Approver')) {
            frm.add_custom_button(__('Approve'), function() {
                frm.trigger('approve_expense');
            }).addClass('btn-primary');
            
            frm.add_custom_button(__('Reject'), function() {
                frm.trigger('reject_expense');
            }).addClass('btn-danger');
            
            frm.add_custom_button(__('Return'), function() {
                frm.trigger('return_expense');
            });
        }
    },

    submit_expense: function(frm) {
        frappe.call({
            method: 'expenses_management.expenses_management.doctype.expense_entry.expense_entry.submit_expense',
            args: {
                docname: frm.doc.name
            },
            callback: function(r) {
                if (!r.exc) {
                    frappe.msgprint(__('Expense entry submitted for approval'));
                    frm.reload_doc();
                }
            }
        });
    },

    approve_expense: function(frm) {
        frappe.call({
            method: 'expenses_management.expenses_management.doctype.expense_entry.expense_entry.approve_expense',
            args: {
                docname: frm.doc.name
            },
            callback: function(r) {
                if (!r.exc) {
                    frappe.msgprint(__('Expense entry approved'));
                    frm.reload_doc();
                }
            }
        });
    },

    reject_expense: function(frm) {
        frappe.prompt([
            {
                fieldname: 'reason',
                label: __('Rejection Reason'),
                fieldtype: 'Small Text',
                reqd: 1
            }
        ],
        function(values) {
            frappe.call({
                method: 'expenses_management.expenses_management.doctype.expense_entry.expense_entry.reject_expense',
                args: {
                    docname: frm.doc.name,
                    reason: values.reason
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.msgprint(__('Expense entry rejected'));
                        frm.reload_doc();
                    }
                }
            });
        },
        __('Reject Expense'),
        __('Submit')
        );
    },

    return_expense: function(frm) {
        frappe.prompt([
            {
                fieldname: 'reason',
                label: __('Return Reason'),
                fieldtype: 'Small Text',
                reqd: 1
            }
        ],
        function(values) {
            frappe.call({
                method: 'expenses_management.expenses_management.doctype.expense_entry.expense_entry.return_expense',
                args: {
                    docname: frm.doc.name,
                    reason: values.reason
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.msgprint(__('Expense entry returned for revision'));
                        frm.reload_doc();
                    }
                }
            });
        },
        __('Return Expense'),
        __('Submit')
        );
    }
});