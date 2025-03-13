import frappe
from frappe.utils import getdate, date_diff
from datetime import datetime
from collections import deque

@frappe.whitelist()
def get_data(filters=None):
    if filters:
        data = []
        purchase_orders = frappe.db.get_list(
            'Purchase Order',
            filters=filters,
            fields=['transaction_date', 'name', 'po_type', 'supplier', 'schedule_date', 'contact_email', 'uom'],
            order_by='transaction_date desc'
        )

        for po in purchase_orders:
            po_dict = dict(po)
            if po_dict.get('transaction_date') and po_dict.get('schedule_date'):
                transaction_date = getdate(po_dict['transaction_date'])
                schedule_date = getdate(po_dict['schedule_date'])
                po_dict['lead_time_days'] = date_diff(schedule_date, transaction_date)
                po_dict['formatted_transaction_date'] = transaction_date.strftime('%d-%m-%Y')
                po_dict['number_of_days_from_po'] = (datetime.now().date() - transaction_date).days + 1
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

                # Initialize fields for receipt and subcontracting data
                item_dict.update({
                    "purchase_receipt": None,
                    "total_accepted_qty": 0,
                    "total_rework": 0,
                    "total_reject": 0,
                    "total_received_qty": 0,
                    "pending_qty": item.qty,
                    "supplied_qty": 0,
                    "consumed_qty": 0,
                    "rm_balance_qty": 0,
                    "rm_received_qty": 0
                })

                # Add receipt task based on PO type
                if po_dict.get('po_type') == 'Sub-Contract':
                    processing_queue.append({
                        "type": "subcontracting_receipt",
                        "po_name": po_dict["name"],
                        "filter_field": filter_field,
                        "item_code": item.item_code,
                        "item_qty": item.qty,
                        "item_dict": item_dict
                    })
                else:
                    processing_queue.append({
                        "type": "purchase_receipt",
                        "po_name": po_dict["name"],
                        "filter_field": filter_field,
                        "item_code": item.item_code,
                        "item_qty": item.qty,
                        "item_dict": item_dict
                    })

                # Always add subcontracting_order task (for raw material tracking)
                processing_queue.append({
                    "type": "subcontracting_order",
                    "po_name": po_dict["name"],
                    "filter_field": filter_field,
                    "item_code": item.item_code,
                    "item_qty": item.qty,
                    "item_dict": item_dict
                })

            processed_items = set()

            while processing_queue:
                task = processing_queue.popleft()
                item_key = f"{task['item_code']}-{task['po_name']}"

                if item_key in processed_items:
                    continue

                if task["type"] == "purchase_receipt":
                    # Process Purchase Receipts (for non-Sub-contract POs)
                    purchase_receipts = frappe.db.get_list("Purchase Receipt", 
                        filters={"purchase_order": task["po_name"], "docstatus": 1},
                        fields=["name", "posting_date"])

                    total_accepted_qty = 0
                    total_received_qty = 0

                    for pr in purchase_receipts:
                        pr_doc = frappe.get_doc("Purchase Receipt", pr.name)
                        for pr_item in pr_doc.items:
                            if pr_item.item_code == task["item_code"]:
                                total_received_qty += pr_item.qty
                                total_accepted_qty += pr_item.qty

                    task["item_dict"]["total_accepted_qty"] = total_accepted_qty
                    task["item_dict"]["total_received_qty"] = total_received_qty
                    task["item_dict"]["pending_qty"] = max(0, task["item_qty"] - total_accepted_qty)

                elif task["type"] == "subcontracting_receipt":
                    # Process Subcontracting Receipts (for Sub-contract POs)
                    subcontracting_orders = frappe.db.get_list("Subcontracting Order",
                        filters={"purchase_order": task["po_name"]},
                        fields=["name"])

                    so_names = [so.name for so in subcontracting_orders]
                    subcontracting_receipts = frappe.db.get_list("Subcontracting Receipt",
                        filters={"subcontracting_order": ["in", so_names], "docstatus": 1},
                        fields=["name"])

                    total_accepted_qty = 0
                    total_received_qty = 0

                    for sr in subcontracting_receipts:
                        sr_doc = frappe.get_doc("Subcontracting Receipt", sr.name)
                        for sr_item in sr_doc.items:
                            if sr_item.item_code == task["filter_field"]:
                                total_received_qty += sr_item.qty
                                total_accepted_qty += sr_item.qty

                    task["item_dict"]["total_accepted_qty"] = total_accepted_qty
                    task["item_dict"]["total_received_qty"] = total_received_qty
                    task["item_dict"]["pending_qty"] = max(0, task["item_qty"] - total_accepted_qty)

                data.append(task["item_dict"])
                processed_items.add(item_key)

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
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        frappe.msgprint(f"Error sending email: {str(e)}")
        return {"status": "error", "message": str(e)}
