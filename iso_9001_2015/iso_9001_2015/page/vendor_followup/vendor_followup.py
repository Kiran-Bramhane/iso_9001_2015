# import frappe
# from frappe.utils import getdate, date_diff
# from datetime import datetime
# from collections import deque

# @frappe.whitelist()
# def get_data(filters=None):
#     if filters:
#         data = []
#         purchase_orders = frappe.db.get_list('Purchase Order', 
#             filters=filters,
#             fields=['transaction_date', 'name', 'po_type', 'supplier', 'schedule_date', 'contact_email', 'uom'],
#             order_by='transaction_date desc'
#         )

#         for po in purchase_orders:
#             po_dict = dict(po)
#             if po_dict.get('transaction_date') and po_dict.get('schedule_date'):
#                 transaction_date = getdate(po_dict['transaction_date'])
#                 schedule_date = getdate(po_dict['schedule_date'])
#                 po_dict['lead_time_days'] = date_diff(schedule_date, transaction_date)
#                 po_dict['formatted_transaction_date'] = transaction_date.strftime('%d-%m-%Y')
#                 po_dict['number_of_days_from_po'] = ((datetime.now().date() - transaction_date).days) + 1
#             else:
#                 po_dict['formatted_transaction_date'] = None
#                 po_dict['number_of_days_from_po'] = None

#             purchase_order_doc = frappe.get_doc("Purchase Order", po_dict["name"])
#             items = purchase_order_doc.items

#             processing_queue = deque()
            
#             for item in items:
#                 item_dict = dict(po_dict)
#                 item_dict["item_name"] = item.item_name
#                 item_dict["item_code"] = item.item_code
#                 item_dict["qty"] = item.qty
#                 item_dict["fg_item"] = item.fg_item
#                 item_dict["uom"] = item.uom
                
#                 filter_field = item.fg_item if item.fg_item else item.item_code
                
#                 item_dict.update({
#                     "purchase_receipt": None,
#                     "total_accepted_qty": 0,
#                     "total_rework": 0,
#                     "total_reject": 0,
#                     "total_received_qty": 0,
#                     "pending_qty": item.qty,
#                     "supplied_qty": 0,
#                     "consumed_qty": 0,
#                     "rm_balance_qty": 0,
#                     "rm_received_qty": 0
#                 })
                
#                 if po_dict.get('po_type') == 'Sub-Contract':
#                     processing_queue.append({
#                         "type": "subcontracting_receipt",
#                         "po_name": po_dict["name"],
#                         "filter_field": filter_field,
#                         "item_code": item.item_code,
#                         "item_qty": item.qty,
#                         "item_dict": item_dict
#                     })
#                 else:
#                     processing_queue.append({
#                         "type": "purchase_receipt",
#                         "po_name": po_dict["name"],
#                         "filter_field": filter_field,
#                         "item_code": item.item_code,
#                         "item_qty": item.qty,
#                         "item_dict": item_dict
#                     })
                
#                 processing_queue.append({
#                     "type": "subcontracting_order",
#                     "po_name": po_dict["name"],
#                     "filter_field": filter_field,
#                     "item_code": item.item_code,
#                     "item_qty": item.qty,
#                     "item_dict": item_dict
#                 })
                
#             processed_items = set()
            
#             while processing_queue:
#                 task = processing_queue.popleft()
#                 item_key = f"{task['item_code']}-{task['po_name']}"
                
#                 if item_key in processed_items:
#                     continue
                
#                 if task["type"] == "purchase_receipt":
#                     purchase_receipts = frappe.db.get_list("Purchase Receipt", 
#                         filters={"purchase_order": task["po_name"], "docstatus": 1},
#                         fields=["name", "posting_date"]
#                     )
                    
#                     total_accepted_qty = 0
#                     total_received_qty = 0
                    
#                     for pr in purchase_receipts:
#                         pr_doc = frappe.get_doc("Purchase Receipt", pr.name)
#                         for pr_item in pr_doc.items:
#                             if pr_item.item_code == task["item_code"]:
#                                 total_received_qty += pr_item.qty
#                                 total_accepted_qty += pr_item.qty
                    
#                     task["item_dict"]["total_accepted_qty"] = total_accepted_qty
#                     task["item_dict"]["total_received_qty"] = total_received_qty
#                     task["item_dict"]["pending_qty"] = max(0, task["item_qty"] - total_accepted_qty)
                
#                 elif task["type"] == "subcontracting_receipt":
#                     subcontracting_orders = frappe.db.get_list("Subcontracting Order",
#                         filters={"purchase_order": task["po_name"]},
#                         fields=["name"]
#                     )
                    
#                     so_names = [so.name for so in subcontracting_orders]
#                     subcontracting_receipts = frappe.db.get_list("Subcontracting Receipt",
#                         filters={"subcontracting_order": ["in", so_names], "docstatus": 1},
#                         fields=["name"]
#                     )
                    
#                     total_accepted_qty = 0
#                     total_received_qty = 0
                    
#                     for sr in subcontracting_receipts:
#                         sr_doc = frappe.get_doc("Subcontracting Receipt", sr.name)
#                         for sr_item in sr_doc.items:
#                             if sr_item.item_code == task["filter_field"]:
#                                 total_received_qty += sr_item.qty
#                                 total_accepted_qty += sr_item.qty
                    
#                     task["item_dict"]["total_accepted_qty"] = total_accepted_qty
#                     task["item_dict"]["total_received_qty"] = total_received_qty
#                     task["item_dict"]["pending_qty"] = max(0, task["item_qty"] - total_accepted_qty)
                
#                 data.append(task["item_dict"])
#                 processed_items.add(item_key)
        
#         return data
#     else:
#         frappe.msgprint("No filters provided.")


# def send_supplier_email(supplier_email, subject, message):
#     if not supplier_email:
#         frappe.msgprint("Error: Supplier email is missing")
#         return {"status": "error", "message": "Supplier email is missing"}
    
#     try:
#         frappe.sendmail(
#             recipients=supplier_email,
#             sender=frappe.session.user,
#             subject=subject,
#             content=message,
#             send_email=True,
#         )
#         frappe.msgprint(f"Email successfully sent to {supplier_email}")
#         return {"status": "success", "message": "Email sent successfully"}
#     except Exception as e:
#         frappe.msgprint(f"Error sending email: {str(e)}")
#         return {"status": "error", "message": str(e)}



























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
                if po_dict.get('po_type') == 'Sub-Contract':  # Corrected PO type check
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

            # Track processed items to avoid duplicates
            processed_items = set()

            while processing_queue:
                task = processing_queue.popleft()
                item_key = f"{task['item_code']}-{task['po_name']}"

                # Skip if item already processed
                if item_key in processed_items:
                    continue

                if task["type"] == "purchase_receipt":
                    # Process Purchase Receipts (for non-Sub-contract POs)
                    purchase_receipts = frappe.db.get_list("Purchase Receipt", 
                                                           filters={"purchase_order": task["po_name"], "docstatus": 1},
                                                           fields=["name", "posting_date"])
                    frappe.msgprint(f"Found {len(purchase_receipts)} Purchase Receipts for PO {task['po_name']}")


                    # Initialize totals for accepted and received quantities
                    total_accepted_qty = 0
                    total_received_qty = 0

                    for pr in purchase_receipts:
                        pr_doc = frappe.get_doc("Purchase Receipt", pr.name)
                        for pr_item in pr_doc.items:
                            if pr_item.item_code == task["item_code"]:
                                # Add to total received quantity
                                total_received_qty += pr_item.qty
                                total_accepted_qty += pr_item.qty
                                frappe.msgprint(f"Purchase Receipt {pr.name}: Received {pr_item.qty} for item {task['item_code']}")

                                # Fetch QA inspections for this item
                                qa_inspections = frappe.db.get_list("QA Inspection",
                                                                    filters={
                                                                        "reference_name": pr.name,
                                                                        "item_code": task["item_code"],
                                                                        "docstatus": 1
                                                                    },
                                                                    fields=["total_accepted_qty", "total_rework", "total_reject", "total_received_qty"])
                                frappe.msgprint(f"Found {len(qa_inspections)} QA Inspections for PR {pr.name}")


                    # Update the item_dict with the aggregated totals
                    task["item_dict"]["total_accepted_qty"] = total_accepted_qty
                    task["item_dict"]["total_received_qty"] = total_received_qty
                    task["item_dict"]["pending_qty"] = max(0, task["item_qty"] - total_accepted_qty)

                    frappe.msgprint(f"Final Totals for Item {task['item_code']}: "
                                   f"Total Accepted Qty = {total_accepted_qty}, "
                                   f"Total Received Qty = {total_received_qty}, "
                                   f"Pending Qty = {task['item_dict']['pending_qty']}")

                elif task["type"] == "subcontracting_receipt":
                    # Process Subcontracting Receipts (for Sub-contract POs)
                    subcontracting_orders = frappe.db.get_list("Subcontracting Order",
                                                              filters={"purchase_order": task["po_name"]},
                                                              fields=["name"])
                    frappe.msgprint(f"Found {len(subcontracting_orders)} Subcontracting Orders for PO {task['po_name']}")

                    so_names = [so.name for so in subcontracting_orders]
                    subcontracting_receipts = frappe.db.get_list("Subcontracting Receipt",
                                                                filters={"subcontracting_order": ["in", so_names], "docstatus": 1},
                                                                fields=["name"])
                    frappe.msgprint(f"Found {len(subcontracting_receipts)} Subcontracting Receipts for PO {task['po_name']}")

                    # Initialize totals for accepted and received quantities
                    total_accepted_qty = 0
                    total_received_qty = 0

                    for sr in subcontracting_receipts:
                        sr_doc = frappe.get_doc("Subcontracting Receipt", sr.name)
                        for sr_item in sr_doc.items:
                            if sr_item.item_code == task["filter_field"]:
                                # Add to total received quantity
                                total_received_qty += sr_item.qty
                                total_accepted_qty += sr_item.qty
                                frappe.msgprint(f"Subcontracting Receipt {sr.name}: Received {sr_item.qty} for FG item {task['filter_field']}")

                                # Fetch QA inspections for this item
                                qa_inspections = frappe.db.get_list("QA Inspection",
                                                                    filters={
                                                                        "reference_name": sr.name,
                                                                        "item_code": task["filter_field"],
                                                                        "docstatus": 1
                                                                    },
                                                                    fields=["total_accepted_qty", "total_rework", "total_reject", "total_received_qty"])
                                frappe.msgprint(f"Found {len(qa_inspections)} QA Inspections for SR {sr.name}")


                    # Update the item_dict with the aggregated totals
                    task["item_dict"]["total_accepted_qty"] = total_accepted_qty
                    task["item_dict"]["total_received_qty"] = total_received_qty
                    task["item_dict"]["pending_qty"] = max(0, task["item_qty"] - total_accepted_qty)

                    frappe.msgprint(f"Final Totals for FG Item {task['filter_field']}: "
                                   f"Total Accepted Qty = {total_accepted_qty}, "
                                   f"Total Received Qty = {total_received_qty}, "
                                   f"Pending Qty = {task['item_dict']['pending_qty']}")

                elif task["type"] == "subcontracting_order":
                    # Process Subcontracting Orders (raw material tracking)
                    subcontracting_orders = frappe.db.get_list("Subcontracting Order",
                                                              filters={"purchase_order": task["po_name"]},
                                                              fields=["name"])
                    frappe.msgprint(f"Processing Subcontracting Order for PO {task['po_name']}")

                    for so in subcontracting_orders:
                        supplied_items = frappe.db.get_all("Subcontracting Order Supplied Item",
                                                            filters={"parent": so.name, "main_item_code": task['filter_field']},
                                                            fields=["supplied_qty", "consumed_qty", "stock_uom"])
                        frappe.msgprint(f"Found {len(supplied_items)} Supplied Items for SO {so.name} with main_item {task['filter_field']}")

                        total_supplied = sum(item.supplied_qty for item in supplied_items)
                        total_consumed = sum(item.consumed_qty for item in supplied_items)

                        task["item_dict"]["supplied_qty"] += total_supplied
                        task["item_dict"]["consumed_qty"] += total_consumed
                        task["item_dict"]["rm_balance_qty"] = round(total_supplied - total_consumed, 3)
                        task["item_dict"]["rm_received_qty"] = round(total_consumed, 3)

                        # Update UOM if available
                        if supplied_items and task["item_dict"].get("fg_item"):
                            task["item_dict"]["uom"] = supplied_items[0].stock_uom

                    # Add to data only after all processing
                    data.append(task["item_dict"])
                    processed_items.add(item_key)
                    frappe.msgprint(f"Added item {task['item_code']} to data with PO {task['po_name']}")

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











