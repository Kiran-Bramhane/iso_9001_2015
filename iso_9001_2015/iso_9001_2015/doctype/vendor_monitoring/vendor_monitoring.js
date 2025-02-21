// // Copyright (c) 2024, Kiran and contributors
// // For license information, please see license.txt

// // frappe.ui.form.on("Vendor Monitoring", {
// // 	refresh(frm) {

// // 	},
// // });


// frappe.ui.form.on('Vendor Monitoring', {
//     general_templates: function(frm) {
//         if (frm.doc.general_templates) {
//             frappe.db.get_doc('General Template', frm.doc.general_templates)
//                 .then(template => {
//                     frm.clear_table('feedback');

//                     if (template.criteria && template.criteria.length > 0) {
//                         template.criteria.forEach(row => {
//                             let child = frm.add_child('feedback');
//                             child.criteria = row.criteria.trim();  // ✅ Trim whitespace
//                             child.rating = row.rating || "";
//                             child.comment = row.comment || "";
//                         });

//                         frm.refresh_field('feedback');
//                         setupRatingChangeListener(frm);
//                     } else {
//                         console.log('No criteria found in the selected template.');
//                     }
//                 })
//                 .catch(() => {
//                     frappe.msgprint(__('Error loading template.'));
//                 });
//         } else {
//             frm.clear_table('feedback');
//             frm.refresh_field('feedback');
//         }
//     },

//     supplier_name: function(frm) {
//         if (!frm.doc.supplier_name) return;

//         console.log("Fetching QA Inspection and Purchase Data for supplier:", frm.doc.supplier_name);

//         frappe.call({
//             method: "get_qa_records",
//             args: {
//                 supplier_name: frm.doc.supplier_name
//             },
//             callback: function(response) {
//                 let data = response.message || {};

//                 if (!data.qa_inspection || data.qa_inspection.length === 0) {
//                     console.log("No QA Inspection records found for this supplier.");
//                     return;
//                 }

//                 console.log("QA Inspection Data:", data);

//                 let total_accepted_qty = 0, total_reject = 0, total_rework = 0;
//                 let total_good = 0, total_bad = 0, total_condition_count = 0;

//                 data.qa_inspection.forEach(row => {
//                     if (row.total_reject !== undefined) total_reject += row.total_reject;
//                     if (row.total_rework !== undefined) total_rework += row.total_rework;
//                     if (row.total_accepted_qty !== undefined) total_accepted_qty += row.total_accepted_qty;
//                     if (row.condition_of_goods_on_arrival) {
//                         total_condition_count++;
//                         row.condition_of_goods_on_arrival === "Good" ? total_good++ : total_bad++;
//                     }
//                 });


//                 let reject_percentage = total_accepted_qty > 0 ? Math.abs((((total_reject / total_accepted_qty) * 100)-100).toFixed(2)) : "0.00";
//                 let rework_percentage = total_accepted_qty > 0 ? Math.abs((((total_rework / total_accepted_qty) * 100)-100).toFixed(2)) : "0.00";
//                 let good_percentage = total_condition_count > 0 ? ((total_good / total_condition_count) * 100).toFixed(2) : "0.00";
                
//                 // ✅ On-Time Delivery Calculation
//                 let total_orders = data.purchase_orders.length;
//                 let on_time_count = 0;

//                 if (total_orders > 0) {
//                     data.purchase_orders.forEach(po => {
//                         let pr = data.purchase_receipts.find(pr => pr.purchase_order === po.name);

//                         if (pr && pr.posting_date) {
//                             let scheduleDate = new Date(po.schedule_date);
//                             let postingDate = new Date(pr.posting_date);

//                             if (postingDate <= scheduleDate) {
//                                 on_time_count++;
//                             }
//                         }
//                     });
//                 }

//                 let on_time_percentage = total_orders > 0 ? ((on_time_count / total_orders) * 100).toFixed(2) : "0.00";

//                 console.log("✅ On-Time Delivery Percentage:", on_time_percentage);

//                 let criteria_map = {
//                     "Rework": parseFloat(rework_percentage),
//                     "Reject": parseFloat(reject_percentage),
//                     "Condition Of Goods On Arrival": parseFloat(good_percentage),
//                     "Delivers On Time": parseFloat(on_time_percentage)  // ✅ Ensure "Delivers On Time" is updated
//                 };

//                 console.log("Criteria Map:", criteria_map);

//                 // ✅ Remove duplicate "Delivers On Time" rows before updating
//                 let existing_rows = {};
//                 let unique_feedback = [];

//                 frm.doc.feedback.forEach(row => {
//                     let key = row.criteria.trim().toLowerCase();
//                     if (!existing_rows[key]) {
//                         existing_rows[key] = row;
//                         unique_feedback.push(row);
//                     } else {
//                         console.log(`❌ Removing duplicate: ${row.criteria}`);
//                     }
//                 });

//                 frm.doc.feedback = unique_feedback; // Assign back only unique rows

//                 let found_delivers_on_time = false;

//                 frm.doc.feedback.forEach(row => {
//                     let criteria_name = row.criteria.trim().toLowerCase();
//                     if (criteria_map[row.criteria] !== undefined) {
//                         row.rating = criteria_map[row.criteria];
//                         console.log(`✅ Updated ${row.criteria} Rating: ${row.rating}`);
//                     }

//                     if (criteria_name === "delivers on time") {
//                         found_delivers_on_time = true;
//                     }
//                 });

//                 if (!found_delivers_on_time) {
//                     console.log("❌ 'Delivers On Time' not found in existing feedback, adding it.");
                    
//                     let child = frm.add_child('feedback');
//                     child.criteria = "Delivers On Time";
//                     child.rating = parseFloat(on_time_percentage);
//                     console.log("✅ Added 'Delivers On Time' in feedback table");
//                 }

//                 frm.refresh_field("feedback");
//                 calculateTotalPercentage(frm);
//             }
//         });
//     },

//     refresh: function(frm) {
//         setupRatingChangeListener(frm);
//     }
// });

// function setupRatingChangeListener(frm) {
//     frm.fields_dict['feedback'].grid.wrapper.on('change', 'input[data-fieldname="rating"]', function() {
//         calculateTotalPercentage(frm);
//     });
// }
// function calculateTotalPercentage(frm) {
//     let total_rating = 0;
//     let total_count = 0;

//     frm.doc.feedback.forEach(row => {
//         let rating_value = parseFloat(row.rating);
//         if (!isNaN(rating_value)) {
//             total_rating += rating_value;
//             total_count++;
//         }
//     });

//     // Calculate the average rating out of 100
//     let total_percentage = total_count > 0 ? Math.abs((total_rating / total_count)) : 0;

//     // Ensure the total percentage is out of 100
//     frm.set_value('total_percentage', total_percentage.toFixed(2));
//     frm.refresh_field('total_percentage');
// }






frappe.ui.form.on('Vendor Monitoring', {
    general_templates: function(frm) {
        if (frm.doc.general_templates) {
            frappe.db.get_doc('General Template', frm.doc.general_templates)
                .then(template => {
                    frm.clear_table('feedback');

                    if (template.criteria && template.criteria.length > 0) {
                        template.criteria.forEach(row => {
                            let child = frm.add_child('feedback');
                            child.criteria = row.criteria.trim();
                            child.rating = row.rating || "";
                            child.comment = row.comment || "";
                        });

                        frm.refresh_field('feedback');
                        setupRatingChangeListener(frm);
                    }
                })
                .catch(() => {
                    frappe.msgprint(__('Error loading template.'));
                });
        } else {
            frm.clear_table('feedback');
            frm.refresh_field('feedback');
        }
    },

    supplier_name: function(frm) {
        if (!frm.doc.supplier_name) return;

        console.log("Fetching QA Inspection and Purchase Data for supplier:", frm.doc.supplier_name);
        frappe.call({
            method: "iso_9001_2015.iso_9001_2015.doctype.vendor_monitoring.vendor_monitoring.get_vendor_monitoring_data",
            args: {
                supplier_name: frm.doc.supplier_name
            },
            callback: function(response) {
                let data = response.message || {};

                if (!data.qa_inspection || data.qa_inspection.length === 0) {
                    console.log("No QA Inspection records found for this supplier.");
                    return;
                }

                console.log("QA Inspection Data:", data);

                let total_accepted_qty = 0, total_reject = 0, total_rework = 0;
                let total_good = 0, total_bad = 0, total_condition_count = 0;

                data.qa_inspection.forEach(row => {
                    total_reject += row.total_reject || 0;
                    total_rework += row.total_rework || 0;
                    total_accepted_qty += row.total_accepted_qty || 0;

                    if (row.condition_of_goods_on_arrival) {
                        total_condition_count++;
                        row.condition_of_goods_on_arrival === "Good" ? total_good++ : total_bad++;
                    }
                });

                let reject_percentage = total_accepted_qty > 0 ? (((total_reject / total_accepted_qty) * 100)-100).toFixed(2) : "0.00";
                let rework_percentage = total_accepted_qty > 0 ? (((total_rework / total_accepted_qty) * 100)-100).toFixed(2) : "0.00";
                let good_percentage = total_condition_count > 0 ? ((total_good / total_condition_count) * 100).toFixed(2) : "0.00";

                // ✅ On-Time Delivery Calculation
                let total_orders = data.purchase_orders.length;
                let on_time_count = 0;

                if (total_orders > 0) {
                    data.purchase_orders.forEach(po => {
                        let pr = data.purchase_receipts.find(pr => pr.purchase_order === po.name);

                        if (pr && pr.posting_date) {
                            let scheduleDate = frappe.datetime.get_date(po.schedule_date);
                            let postingDate = frappe.datetime.get_date(pr.posting_date);

                            if (postingDate <= scheduleDate) {
                                on_time_count++;
                            }
                        }
                    });
                }

                let on_time_percentage = total_orders > 0 ? ((on_time_count / total_orders) * 100).toFixed(2) : "0.00";

                console.log("✅ On-Time Delivery Percentage:", on_time_percentage);

                let criteria_map = {
                    "Rework": parseFloat(rework_percentage),
                    "Reject": parseFloat(reject_percentage),
                    "Condition Of Goods On Arrival": parseFloat(good_percentage),
                    "Delivers On Time": parseFloat(on_time_percentage)
                };

                console.log("Criteria Map:", criteria_map);

                // ✅ Remove duplicate "Delivers On Time" rows before updating
                let feedback_map = {};
                frm.doc.feedback.forEach(row => {
                    let key = row.criteria.trim().toLowerCase();
                    feedback_map[key] = row;
                });

                // ✅ Update ratings for existing criteria
                Object.keys(criteria_map).forEach(criteria => {
                    let key = criteria.toLowerCase();
                    if (feedback_map[key]) {
                        feedback_map[key].rating = criteria_map[criteria];
                        console.log(`✅ Updated ${criteria} Rating: ${feedback_map[key].rating}`);
                    } else {
                        // ✅ Add missing criteria row
                        let child = frm.add_child('feedback');
                        child.criteria = criteria;
                        child.rating = criteria_map[criteria];
                        console.log(`✅ Added ${criteria} in feedback table`);
                    }
                });

                frm.refresh_field("feedback");
                calculateTotalPercentage(frm);
            }
        });
    },

    refresh: function(frm) {
        setupRatingChangeListener(frm);
    }
});

function setupRatingChangeListener(frm) {
    frm.fields_dict['feedback'].grid.wrapper.on('change', 'input[data-fieldname="rating"]', function() {
        calculateTotalPercentage(frm);
    });
}

function calculateTotalPercentage(frm) {
    let total_rating = 0;
    let total_count = 0;

    frm.doc.feedback.forEach(row => {
        let rating_value = parseFloat(row.rating);
        if (!isNaN(rating_value)) {
            total_rating += rating_value;
            total_count++;
        }
    });

    // Calculate the average rating out of 100
    let total_percentage = total_count > 0 ? (total_rating / total_count) : 0;

    // Ensure the total percentage is out of 100
    frm.set_value('total_percentage', total_percentage.toFixed(2));
    frm.refresh_field('total_percentage');
}
