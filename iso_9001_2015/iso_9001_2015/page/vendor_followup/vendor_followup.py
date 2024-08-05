import frappe
from frappe.utils import getdate, date_diff
from datetime import datetime
from frappe.core.doctype.communication.email import make

@frappe.whitelist()
def get_data(filters=None):
    if filters:
        data = frappe.db.get_list('Purchase Order', 
                                  filters=filters,
                                  fields=['transaction_date', 'name', 'supplier', 'schedule_date','contact_email']
        )
        for i in data:
            # Check if both 'transaction_date' and 'schedule_date' are present
            if i.get('transaction_date') and i.get('schedule_date'):
                transaction_date = getdate(i['transaction_date'])
                schedule_date = getdate(i['schedule_date'])

                # Calculate lead time in days
                i['lead_time_days'] = date_diff(schedule_date, transaction_date)

                # Format the transaction date
                formatted_date = transaction_date.strftime('%d-%m-%Y')
                i['formatted_transaction_date'] = formatted_date

                # Calculate the number of days from PO
                current_date = datetime.now().date()
                i['number_of_days_from_po'] = (current_date - transaction_date).days
            else:
                i['formatted_transaction_date'] = None
                i['number_of_days_from_po'] = None

            item_details = frappe.db.get_value("Purchase Order Item", 
                                               filters={"parent": i["name"]},
                                               fieldname=["item_code", "item_name", "qty"],
                                               as_dict=True)
            
            if item_details:
                purchase_receipt = frappe.db.get_value("Purchase Receipt", 
                                                       filters={"purchase_order": i["name"], "docstatus": 1},
                                                       fieldname=["name"],
                                                       as_dict=True)
                
                if purchase_receipt:
                    qa_inspection = frappe.db.get_value("QA Inspection", 
                                                        filters={"reference_name": purchase_receipt["name"]},
                                                        fieldname=["total_accepted_qty", "total_rework", "total_reject", "total_received_qty"],
                                                        as_dict=True)
                    
                    if qa_inspection:
                        i["total_received_qty"]=qa_inspection.get("total_received_qty", 0)
                        i["total_accepted_qty"] = qa_inspection.get("total_accepted_qty", 0)
                        i["total_rework"] = qa_inspection.get("total_rework", 0)
                        i["total_reject"] = qa_inspection.get("total_reject", 0)
                        total_rework = qa_inspection.get("total_rework", 0)
                        total_received_qty = qa_inspection.get("total_received_qty", 0)
                    else:
                        total_rework = 0
                        total_received_qty = 0

                    i["pending_qty"] = abs(item_details.get("qty", 0) - total_rework - total_received_qty)

                i["item_name"] = item_details["item_name"]
                i["item_code"] = item_details["item_code"]
                i["qty"] = item_details["qty"]

        return data
# def send_supplier_email(supplier_email, subject, message):
#     try:
#         make(
#             recipients=supplier_email,
#             sender=frappe.session.user,
#             subject=subject,
#             content=message,
#             send_email=True,
#         )
#         return {"status": "success", "message": "Email sent successfully"}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}





def send_supplier_email(supplier_email, subject, message):
    if not supplier_email:
        return {"status": "error", "message": "Supplier email is missing"}

    try:
        make(
            recipients=supplier_email,
            sender=frappe.session.user,
            subject=subject,
            content=message,
            send_email=True,
        )
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
