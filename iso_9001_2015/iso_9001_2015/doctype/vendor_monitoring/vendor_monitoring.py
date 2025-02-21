# Copyright (c) 2024, Kiran and contributors
# For license information, please see license.txt








# supplier_name = frappe.form_dict.get("supplier_name")

# if not supplier_name:
#     frappe.response["error"] = _("Supplier name is required")
# else:
#     try:
#         # Fetch QA Inspection Data
#         qa_inspection_data = frappe.get_all(
#             "QA Inspection",
#             filters={"source_details": supplier_name},
#             fields=["name", "total_rework", "total_reject", "total_accepted_qty", "condition_of_goods_on_arrival"]
#         )

#         # Fetch Purchase Orders for the Supplier
#         po_data = frappe.get_all(
#             "Purchase Order",
#             filters={"supplier": supplier_name},
#             fields=["name", "schedule_date"]
#         )

#         # Extract PO names for filtering PRs
#         po_names = [po["name"] for po in po_data]

#         # Fetch Purchase Receipts that are **linked to these POs**
#         pr_data = []
#         if po_names:
#             pr_data = frappe.get_all(
#                 "Purchase Receipt",
#                 filters={"purchase_order": ["in", po_names]},
#                 fields=["name", "posting_date", "purchase_order"]
#             )

#         # Convert PR data into a dictionary to ensure **matching PO-PR structure**
#         pr_dict = {pr["purchase_order"]: pr for pr in pr_data}

#         # Ensure PR data **matches** the PO data structure
#         formatted_pr_data = []
#         for po in po_data:
#             pr_entry = pr_dict.get(po["name"], {"name": None, "posting_date": None, "purchase_order": po["name"]})
#             formatted_pr_data.append(pr_entry)

#         # Construct Response
#         frappe.response["message"] = {
#             "qa_inspection": qa_inspection_data,
#             "purchase_orders": po_data,
#             "purchase_receipts": formatted_pr_data  # PR data exactly matching PO data
#         }

#     except Exception as e:
#         frappe.log_error(f"Error fetching data for supplier {supplier_name}: {str(e)}")
#         frappe.response["error"] = _("An error occurred while fetching supplier-related data.")










import frappe
from frappe.model.document import Document

class VendorMonitoring(Document):
    pass  # Keeping the class empty since we are using a whitelisted function

@frappe.whitelist()
def get_vendor_monitoring_data(supplier_name):
    if not supplier_name:
        frappe.throw("Supplier name is required")

    try:
        # Fetch QA Inspection Data
        qa_inspection_data = frappe.get_all(
            "QA Inspection",
            filters={"source_details": supplier_name},
            fields=["name", "total_rework", "total_reject", "total_accepted_qty", "condition_of_goods_on_arrival"]
        )

        # Fetch Purchase Orders for the Supplier
        po_data = frappe.get_all(
            "Purchase Order",
            filters={"supplier": supplier_name},
            fields=["name", "schedule_date"]
        )

        # Extract PO names for filtering PRs
        po_names = [po["name"] for po in po_data]

        # Fetch Purchase Receipts that are **linked to these POs**
        pr_data = []
        if po_names:
            pr_data = frappe.get_all(
                "Purchase Receipt",
                filters={"purchase_order": ["in", po_names]},
                fields=["name", "posting_date", "purchase_order"]
            )

        # Convert PR data into a dictionary to ensure **matching PO-PR structure**
        pr_dict = {pr["purchase_order"]: pr for pr in pr_data}

        # Ensure PR data **matches** the PO data structure
        formatted_pr_data = [
            pr_dict.get(po["name"], {"name": None, "posting_date": None, "purchase_order": po["name"]})
            for po in po_data
        ]

        # Return the response instead of modifying `frappe.response`
        return {
            "qa_inspection": qa_inspection_data,
            "purchase_orders": po_data,
            "purchase_receipts": formatted_pr_data  # PR data exactly matching PO data
        }

    except Exception as e:
        frappe.log_error(f"Error fetching data for supplier {supplier_name}: {str(e)}")
        frappe.throw("An error occurred while fetching supplier-related data.")
