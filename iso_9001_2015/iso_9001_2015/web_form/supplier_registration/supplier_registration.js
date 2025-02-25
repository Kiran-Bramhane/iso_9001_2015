// frappe.ready(function() {
//     frappe.web_form.on('gst_no', (field, value) => {
//         if (value) {
//             frappe.call({
//                 method: "iso_9001_2015.iso_9001_2015.web_form.supplier_registration.supplier_registration.fetch_gst_data",  // Backend API call
//                 args: {
//                     gst_no: value
//                 },
//                 callback: function(response) {
//                     if (response.message) {
//                         let data = response.message.result;
//                         console.log(data)
//                         frappe.web_form.set_value("office_address", data.address1+", "+data.address2);
//                         frappe.web_form.set_value("state_gst_no", data.stateCode);
//                         frappe.web_form.set_value("company", data.legalName);
//                         frappe.web_form.set_value("state", data.stateCode);
//                     } else {
//                         frappe.msgprint("Invalid GST Number");
//                     }
//                 }
//             });
//         }
//     });
// });












// Copyright (c) 2024, Kiran and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Supplier Registration", {
// 	refresh(frm) {

// 	},
// });


// frappe.ready(function() {
//     frappe.web_form.on('gst_no', (field, value) => {
//         if (value) {
//             console.log(value);
//             frappe.call({
//                 method: "iso_9001_2015.iso_9001_2015.web_form.supplier_registration.supplier_registration.fetch_gst_data",  // Backend API call
//                 args: {
//                     gst_no: value
//                 },
//                 callback: function(response) {
//                     if (response.message) {
//                         let data = response.message.result;
//                         console.log(data)
//                         frappe.web_form.set_value("office_address_1", data.address1);
//                         frappe.web_form.set_value("office_address_2", data.address2);
//                         frappe.web_form.set_value("state_gst_no", data.stateCode);
//                         frappe.web_form.set_value("company", data.tradeName);
//                     } else {
//                         frappe.msgprint("Invalid GST Number");
//                     }
//                 }
//             });
//         }
//     });
// });


































frappe.ready(function() {
    frappe.web_form.on('gst_no', (field, value) => {
        if (value) {
            console.log(value);
            frappe.call({
                method: "iso_9001_2015.iso_9001_2015.web_form.supplier_registration.supplier_registration.fetch_gst_data",  // Backend API call
                args: {
                    gst_no: value
                },
                callback: function(response) {
                    if (response.message) {
                        let data = response.message.result;
                        console.log(data);

                        // Define the dictionary mapping GST state codes to state names
                        const stateGSTCodeToName = {
                            '01': 'Jammu & Kashmir',
                            '02': 'Himachal Pradesh',
                            '03': 'Punjab',
                            '04': 'Chandigarh',
                            '05': 'Uttarakhand',
                            '06': 'Haryana',
                            '07': 'Delhi',
                            '08': 'Rajasthan',
                            '09': 'Uttar Pradesh',
                            '10': 'Bihar',
                            '11': 'Sikkim',
                            '12': 'Arunachal Pradesh',
                            '13': 'Nagaland',
                            '14': 'Manipur',
                            '15': 'Mizoram',
                            '16': 'Tripura',
                            '17': 'Meghalaya',
                            '18': 'Assam',
                            '19': 'West Bengal',
                            '20': 'Jharkhand',
                            '21': 'Odisha',
                            '22': 'Chhattisgarh',
                            '23': 'Madhya Pradesh',
                            '24': 'Gujarat',
                            '25': 'Daman and Diu',
                            '26': 'Dadra and Nagar Haveli',
                            '27': 'Maharashtra',
                            '28': 'Goa',
                            '29': 'Karnataka',
                            '30': 'Lakshadweep',
                            '31': 'Kerala',
                            '32': 'Tamil Nadu',
                            '33': 'Puducherry',
                            '34': 'Andaman and Nicobar Islands',
                            '35': 'Telangana',
                            '36': 'Andhra Pradesh',
                            '37': 'Tamil Nadu',
                            '38': 'Kolkata',
                            '39': 'Kochi',
                            '40': 'Gujarat',
                            '41': 'Madhya Pradesh',
                            '42': 'Maharashtra',
                            '43': 'Uttarakhand',
                            '44': 'Delhi',
                            '45': 'Chhattisgarh',
                            '46': 'Rajasthan',
                            '47': 'Puducherry'
                        };

                        // Get the state name based on the state GST code
                        let stateName = stateGSTCodeToName[data.stateCode];

                        if (stateName) {
                            // Set the state name in the form
                            frappe.web_form.set_value("state", stateName);
                        } else {
                            frappe.web_form.set_value("state", 'Unknown State'); // Default value if state code is not found
                        }

                        // Set other values as before
                        frappe.web_form.set_value("office_address_1", data.address1);
                        frappe.web_form.set_value("office_address_2", data.address2);
                        frappe.web_form.set_value("state_gst_no", data.stateCode);
                        frappe.web_form.set_value("company", data.tradeName);
                    } else {
                        frappe.msgprint("Invalid GST Number");
                    }
                }
            });
        }
    });
});
