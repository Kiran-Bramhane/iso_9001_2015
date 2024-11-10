
import frappe
from frappe.utils import getdate, date_diff
from datetime import datetime
from collections import deque

@frappe.whitelist()
def get_data(filters=None):
    if filters:
        data = []
        purchase_orders = frappe.db.get_list('Purchase Order', 
                                             filters=filters,
                                             fields=['transaction_date', 'name', 'supplier', 'schedule_date', 'contact_email', 'uom'],
                                             order_by='transaction_date desc'
        )

        for po in purchase_orders:
            po_dict = dict(po)
            if po_dict.get('transaction_date') and po_dict.get('schedule_date'):
                transaction_date = getdate(po_dict['transaction_date'])
                schedule_date = getdate(po_dict['schedule_date'])

                po_dict['lead_time_days'] = date_diff(schedule_date, transaction_date)
                po_dict['formatted_transaction_date'] = transaction_date.strftime('%d-%m-%Y')
                po_dict['number_of_days_from_po'] = ((datetime.now().date() - transaction_date).days) + 1
            else:
                po_dict['formatted_transaction_date'] = None
                po_dict['number_of_days_from_po'] = None

            purchase_order_doc = frappe.get_doc("Purchase Order", po_dict["name"])
            items = purchase_order_doc.items

            processing_queue = deque()

            for item in items:
                item_dict = dict(po_dict)
                item_dict["item_name"] = item.item_name
                item_dict["item_code"] = item.item_code
                item_dict["qty"] = item.qty
                item_dict["fg_item"] = item.fg_item
                item_dict["uom"] = item.uom

                filter_field = item.fg_item if item.fg_item else item.item_code

                # Initialize item_dict fields for purchase receipt and subcontracting
                item_dict["purchase_receipt"] = None
                item_dict["total_accepted_qty"] = 0
                item_dict["total_rework"] = 0
                item_dict["total_reject"] = 0
                item_dict["total_received_qty"] = 0
                item_dict["pending_qty"] = item.qty
                item_dict["supplied_qty"] = 0
                item_dict["consumed_qty"] = 0

                # Add the processing of purchase receipt to the queue
                processing_queue.append({
                    "type": "purchase_receipt",
                    "po_name": po_dict["name"],
                    "filter_field": filter_field,
                    "item_code": item.item_code,
                    "item_qty": item.qty,
                    "item_dict": item_dict
                })

                # Add the processing of subcontracting orders to the queue
                processing_queue.append({
                    "type": "subcontracting_order",
                    "po_name": po_dict["name"],
                    "filter_field": filter_field,
                    "item_code": item.item_code,
                    "item_qty": item.qty,
                    "item_dict": item_dict
                })

            while processing_queue:
                task = processing_queue.popleft()

                if task["type"] == "purchase_receipt":
                    purchase_receipts = frappe.db.get_list("Purchase Receipt", 
                                                           filters={"purchase_order": task["po_name"], "docstatus": 1},
                                                           fields=["name", "posting_date"])

                    if purchase_receipts:
                        for pr in purchase_receipts:
                            pr_dict = dict(pr)
                            purchase_receipt_doc = frappe.get_doc("Purchase Receipt", pr_dict["name"])
                            pr_items = purchase_receipt_doc.items

                            for pr_item in pr_items:
                                if pr_item.item_code == task["item_code"]:
                                    task["item_dict"]["purchase_receipt"] = pr_dict["name"]

                                    # Get QA inspections for this Purchase Receipt item
                                    qa_inspections = frappe.db.get_list("QA Inspection", 
                                                                        filters={
                                                                            "reference_name": pr_dict["name"], 
                                                                            "item_code": ["like", f"%{task['filter_field'].strip()}%"],
                                                                            "docstatus": 1
                                                                        },
                                                                        fields=["name", "total_accepted_qty", "total_rework", "total_reject", "total_received_qty"])

                                    # Aggregate QA inspection results
                                    for qa in qa_inspections:
                                        task["item_dict"]["total_accepted_qty"] += qa["total_accepted_qty"] or 0
                                        task["item_dict"]["total_rework"] += qa["total_rework"] or 0
                                        task["item_dict"]["total_reject"] += qa["total_reject"] or 0
                                        task["item_dict"]["total_received_qty"] += qa["total_received_qty"] or 0

                                        task["item_dict"]["pending_qty"] = round(task["item_qty"] - task["item_dict"]["total_accepted_qty"], 3)

                elif task["type"] == "subcontracting_order":
                    subcontracting_orders = frappe.db.get_list(
                        "Subcontracting Order", 
                        filters={"purchase_order": task["po_name"]},
                        fields=["name"]
                    )

                    if subcontracting_orders:
                        for so in subcontracting_orders:
                            supplied_items = frappe.db.get_all(
                                "Subcontracting Order Supplied Item", 
                                filters={
                                    "parent": so["name"], 
                                    "main_item_code": ["like", f"%{task['filter_field'].strip()}%"]
                                },
                                fields=["supplied_qty", "consumed_qty", "stock_uom", "main_item_code"]
                            )

                            total_supplied_qty = 0
                            total_consumed_qty = 0
                            subcontracting_stock_uom = None

                            for supplied_item in supplied_items:
                                total_supplied_qty += supplied_item.get("supplied_qty", 0)
                                total_consumed_qty += supplied_item.get("consumed_qty", 0)

                                # Set stock_uom from Subcontracting Order Supplied Item if it's an FG item
                                if item.fg_item:
                                    subcontracting_stock_uom = supplied_item.get("stock_uom", None)

                            # Update the task dictionary
                            task["item_dict"]["supplied_qty"] = total_supplied_qty
                            task["item_dict"]["consumed_qty"] = total_consumed_qty
                            task["item_dict"]["rm_balance_qty"] = round(total_supplied_qty - total_consumed_qty, 3)
                            task["item_dict"]["rm_received_qty"] = round(total_consumed_qty - task["item_dict"].get("total_received_qty", 0), 3)

                            # If stock_uom is found in Subcontracting Order Supplied Item, override the existing uom
                            if subcontracting_stock_uom:
                                task["item_dict"]["uom"] = subcontracting_stock_uom

                # Append the processed item_dict to data once all processing is done
                if task["type"] == "subcontracting_order":
                    data.append(task["item_dict"])

        return data
    else:
        frappe.msgprint("No filters provided.")


def send_supplier_email(supplier_email, subject, message):
    if not supplier_email:
        frappe.msgprint("Error: Supplier email is missing")
        return {"status": "error", "message": "Supplier email is missing"}

    try:
        frappe.sendmail(
            recipients=supplier_email,
            sender=frappe.session.user,
            subject=subject,
            content=message,
            send_email=True,
        )
        frappe.msgprint(f"Email successfully sent to {supplier_email}")
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        frappe.msgprint(f"Error sending email: {str(e)}")
        return {"status": "error", "message": str(e)}



