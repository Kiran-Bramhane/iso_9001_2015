frappe.pages["vendor-followup"].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "Vendor Follow-Up",
        single_column: true,
    });

    let container = $('<div>').appendTo(page.body);

    function load_data() {
        let supplier = page.supplier_field.get_value();
        let from_date = page.from_date_field.get_value();
        let to_date = page.to_date_field.get_value();
        get_data(supplier, from_date, to_date).then((supplierData) => {
            render_data(supplierData);
        }).catch((err) => {
            console.log("Error fetching data:", err);
        });
    }

    // Add filters
    page.from_date_field = page.add_field({
        fieldname: 'from_date',
        label: __('From Date'),
        fieldtype: 'Date',
        change: function() {
            load_data();
        },
    });

    page.to_date_field = page.add_field({
        fieldname: 'to_date',
        label: __('To Date'),
        fieldtype: 'Date',
        change: function() {
            load_data();
        },
    });

    page.supplier_field = page.add_field({
        fieldname: 'supplier',
        label: __('Supplier'),
        fieldtype: 'Link',
        options: 'Supplier',
        change: function() {
            load_data();
        },
    });

    function get_data(supplier, from_date, to_date) {
        let filters = {
            docstatus: 1,
            status: ["in", ["To Receive and Bill", "To Receive"]]
        };

        if (supplier) {
            filters["supplier"] = supplier;
        }
        if (from_date && to_date) {
            filters["transaction_date"] = ["between", [from_date, to_date]];
        } else if (to_date) {
            filters["transaction_date"] = ["<=", to_date];
        } else if (from_date) {
            filters["transaction_date"] = [">=", from_date];
        }

        return frappe.call({
            method: 'iso_9001_2015.iso_9001_2015.page.vendor_followup.vendor_followup.get_data',
            args: { filters: filters }
        }).then((response) => {
            return response.message || [];
        }).catch((err) => {
            console.log("Error fetching data:", err);
            return [];
        });
    }

    function render_data(data) {
        data.forEach((item, index) => {
            item.index = index + 1;
        });

        let html = frappe.render_template("vendor_followup", {
            purchase_orders: data,
        });
        container.html(html);

        container.find('.msgprint-btn').click(function() {
            var button = $(this);
            var supplier = button.data('supplier');
            var email = button.data('email');

            var d = new frappe.ui.Dialog({
                title: 'Enter details',
                fields: [
                    {
                        label: 'Supplier Name',
                        fieldname: 'supplier_name',
                        fieldtype: 'Data',
                        default: supplier,
                        read_only: 1
                    },
                    {
                        label: 'Supplier Email',
                        fieldname: 'contact_email',
                        fieldtype: 'Data',
                        default: email,
                        read_only: 1
                    },
                    {
                        label: 'Email',
                        fieldname: 'email',
                        fieldtype: 'Text'
                    }
                ],
                size: 'small',
                primary_action_label: 'Send',
                primary_action(values) {
                    if (!values.contact_email) {
                        frappe.msgprint('Supplier email is required');
                        return;
                    }
            
                    frappe.call({
                        method: 'iso_9001_2015.iso_9001_2015.page.vendor_followup.vendor_followup.send_supplier_email',
                        args: {
                            supplier_email: values.contact_email,
                            subject: 'Follow Up',
                            message: values.email
                        },
                        callback: function(r) {
                            if (r.message.status === 'success') {
                                frappe.msgprint('Email sent successfully');
                            } else {
                                frappe.msgprint('Error sending email: ' + r.message.message);
                            }
                            d.hide();
                        }
                    });
                }
            });
            d.show();
        });

    }
    load_data();
};
