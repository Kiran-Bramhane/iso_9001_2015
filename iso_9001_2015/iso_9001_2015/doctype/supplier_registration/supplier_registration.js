// Copyright (c) 2024, Kiran and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Supplier Registration", {
// 	refresh(frm) {

// 	},
// });







frappe.ui.form.on('Supplier Registration', {
    gst_no: function(frm) {
        if (frm.doc.gst_no) {
            frappe.call({
                method: "iso_9001_2015.iso_9001_2015.doctype.supplier_registration.supplier_registration.get_gst_details",
                args: { gst_no: frm.doc.gst_no }, // Use `gst_no` as per Python function
                callback: function(response) {
                    if (response.message && response.message.data && response.message.data.details) {
                        frm.set_value('office_address', response.message.data.details.gstinstatus);
                    } else {
                        frappe.msgprint(__('Invalid response from GST API.'));
                    }
                },
                error: function(err) {
                    frappe.msgprint(__('Error fetching GST details.'));
                }
            });
        }
    }
});
