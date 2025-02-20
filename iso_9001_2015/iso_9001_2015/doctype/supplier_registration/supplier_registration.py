# Copyright (c) 2024, Kiran and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SupplierRegistration(Document):
    def before_validate(self):
        # Validate PAN Number (Format: ABCDE1234F)
        if self.pan_no:
            if len(self.pan_no) != 10 or not (self.pan_no[:5].isalpha() and self.pan_no[5:9].isdigit() and self.pan_no[9].isalpha()):
                frappe.throw(f"Invalid PAN Number format: {self.pan_no}. Example: 'ABCDE1234F' (5 letters, 4 digits, 1 letter)")

        # Validate Email ID (Basic check for '@' and '.')
        if self.email_id:
            if "@" not in self.email_id or "." not in self.email_id.split("@")[-1]:
                frappe.throw(f"Invalid Email ID: {self.email_id}. Example: 'example@email.com' (must contain '@' and a valid domain)")

        # Validate Account Number (Must be numeric and 9-18 digits)
        if self.account_number:
            if not self.account_number.isdigit() or not (9 <= len(self.account_number) <= 18):
                frappe.throw(f"Invalid Account Number: {self.account_number}. Example: '123456789' (must be 9 to 18 digits long)")

        # Validate MSME Number (Assuming it should be alphanumeric with 12 characters)
        if self.msme_no:
            if len(self.msme_no) != 12 or not self.msme_no.isalnum():
                frappe.throw(f"Invalid MSME Number: {self.msme_no}. Example: 'UAN1234567890' (12-character alphanumeric code)")

        # Validate IFSC Code (Format: 4 letters followed by 7 alphanumeric characters)
        if self.ifsc_code:
            if len(self.ifsc_code) != 11 or not (self.ifsc_code[:4].isalpha() and self.ifsc_code[4] == "0" and self.ifsc_code[5:].isalnum()):
                frappe.throw(f"Invalid IFSC Code: {self.ifsc_code}. Example: 'SBIN0001234' (4 letters, '0', and 7 alphanumeric characters)")

        # Validate GST Number (Format: 2-digit state code + PAN + 3-digit suffix)
        if self.gst_no:
            if len(self.gst_no) != 15 or not (self.gst_no[:2].isdigit() and 
                                              self.gst_no[2:12].isalnum() and 
                                              self.gst_no[2:7].isalpha() and 
                                              self.gst_no[7:11].isdigit() and 
                                              self.gst_no[11].isalpha() and 
                                              self.gst_no[12:].isalnum()):
                frappe.throw(f"Invalid GST Number: {self.gst_no}. Example: '27ABCDE1234F1Z5' (2 digits for state, PAN format, 3-digit suffix)")

        # Required document validation
        required_documents = ["MSME Certificate", "Cancel Cheque", "Pan Card"]

        # Ensure document_attachment is not None before iterating
        if not self.get("document_attachment"):
            frappe.throw("Please attach the required documents.")

        # Check if all required documents are attached
        attached_documents = set()
        for doc_attachment in self.document_attachment:
            # Ensure document is selected
            if not doc_attachment.documents:
                frappe.throw(f"Please attach the document for '{doc_attachment.name1}' in the document attachment table.")

            # Track attached required documents
            if doc_attachment.name1 in required_documents:
                attached_documents.add(doc_attachment.name1)

        # Identify missing required documents
        missing_documents = [doc for doc in required_documents if doc not in attached_documents]
        if missing_documents:
            frappe.throw(f"Please attach the required documents: {', '.join(missing_documents)}")
