frappe.pages["vendor-followup"].on_page_load = function (wrapper) {
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
        let po_type = page.po_type_field.get_value();
        let status = page.status_field.get_value();

        get_data(supplier, from_date, to_date, po_type, status).then((supplierData) => {
            render_data(supplierData);
        }).catch((err) => {
            console.log("Error fetching data:", err);
        });
    }

    // Add filters
    page.from_date_field = page.add_field({
        fieldname: 'from_date',
        label: __('From Date'),
        fieldtype: 'Date'
    });

    page.to_date_field = page.add_field({
        fieldname: 'to_date',
        label: __('To Date'),
        fieldtype: 'Date'
    });

    page.supplier_field = page.add_field({
        fieldname: 'supplier',
        label: __('Supplier'),
        fieldtype: 'Link',
        options: 'Supplier'
    });

    page.po_type_field = page.add_field({
        fieldname: 'po_type',
        label: __('PO Type'),
        fieldtype: 'Select',
        options: ["",'Capital', 'Consumable', 'Expense', 'Others', 'Return', 'Rework', 'Sub-Contract'].join('\n') // Change these options as needed
    });

    page.status_field = page.add_field({
        fieldname: 'status',
        label: __('Status'),
        fieldtype: 'Select',
        options: ["",'To Receive and Bill', 'To Receive'].join('\n')
    });

    // // // Add Search button
    // page.search_button = page.add_field({
    //     fieldname: 'search',
    //     label: __('Search'),
    //     fieldtype: 'Button',
    //     click: function () {
    //         load_data();
    //     }
    // });

    // // Add a Bootstrap class to the button
    // page.search_button.$wrapper.addClass('btn btn-light');




    // Add Search button with Bootstrap class from the start
    page.search_button = page.add_field({
        fieldname: 'search',
        label: __('Search'),
        fieldtype: 'Button',
        click: function () {
                load_data();
            }
    });

    // Apply Bootstrap and custom class immediately
    page.search_button.$wrapper.addClass('btn custom-search-btn');

    // Add custom styles at creation
    const style = document.createElement('style');
    style.innerHTML = `
        .custom-search-btn button {
            background-color: #007bff; /* Blue background */
            color: white; /* White text */
            border: 1px solid #0056b3;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0px 4px 6px rgba(0, 123, 255, 0.3);
        }

        .custom-search-btn button:hover {
            background-color: #0056b3;
            color: white;
            box-shadow: 0px 6px 10px rgba(0, 91, 187, 0.5);
        }

        .custom-search-btn button:active {
            background-color: #004494;
            color: white;
            transform: scale(0.95);
            box-shadow: 0px 2px 6px rgba(0, 68, 148, 0.5);
        }
    `;
    document.head.appendChild(style);




    function get_data(supplier, from_date, to_date, po_type, status) {
        let filters = {
            docstatus: 1
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

        if (po_type) {
            filters["po_type"] = po_type;
        }

        if (status) {
            filters["status"] = status;
        } else {
            filters["status"] = ["in", ["To Receive and Bill", "To Receive"]];
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

        container.find('.msgprint-btn').click(function () {
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
                        callback: function (r) {
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
   // Initial Data Load - Load all data only if no filters are applied
   setTimeout(() => {
        if (!is_filtered) {
            load_data();
        }
    }, 500); // Small delay to ensure filters are not set yet
};
