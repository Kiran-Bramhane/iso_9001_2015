# Copyright (c) 2024, Kiran and contributors
# For license information, please see license.txt






# # Validate PAN Number (Format: ABCDE1234F)
# if doc.pan_no:
#     if len(doc.pan_no) != 10 or not (doc.pan_no[:5].isalpha() and doc.pan_no[5:9].isdigit() and doc.pan_no[9].isalpha()):
#         frappe.throw(f"Invalid PAN Number format: {doc.pan_no}. Example: 'ABCDE1234F' (5 letters, 4 digits, 1 letter)")

# # Validate Email ID (Basic check for '@' and '.')
# if doc.email_id:
#     if "@" not in doc.email_id or "." not in doc.email_id.split("@")[-1]:
#         frappe.throw(f"Invalid Email ID: {doc.email_id}. Example: 'example@email.com' (must contain '@' and a valid domain)")

# # Validate Account Number (Must be numeric and 9-18 digits)
# if doc.account_number:
#     if not doc.account_number.isdigit() or not (9 <= len(doc.account_number) <= 18):
#         frappe.throw(f"Invalid Account Number: {doc.account_number}. Example: '123456789' (must be 9 to 18 digits long)")

# # Validate MSME Number (Assuming it should be alphanumeric with 12 characters)
# if doc.msme_no:
#     if len(doc.msme_no) != 12 or not doc.msme_no.isalnum():
#         frappe.throw(f"Invalid MSME Number: {doc.msme_no}. Example: 'UAN1234567890' (12-character alphanumeric code)")

# # Validate IFSC Code (Format: 4 letters followed by 7 alphanumeric characters)
# if doc.ifsc_code:
#     if len(doc.ifsc_code) != 11 or not (doc.ifsc_code[:4].isalpha() and doc.ifsc_code[4] == "0" and doc.ifsc_code[5:].isalnum()):
#         frappe.throw(f"Invalid IFSC Code: {doc.ifsc_code}. Example: 'SBIN0001234' (4 letters, '0', and 7 alphanumeric characters)")

# # Validate GST Number (Format: 2-digit state code + PAN + 3-digit suffix)
# if doc.gst_no:
#     if len(doc.gst_no) != 15 or not (doc.gst_no[:2].isdigit() and 
#                                      doc.gst_no[2:12].isalnum() and 
#                                      doc.gst_no[2:7].isalpha() and 
#                                      doc.gst_no[7:11].isdigit() and 
#                                      doc.gst_no[11].isalpha() and 
#                                      doc.gst_no[12:].isalnum()):
#         frappe.throw(f"Invalid GST Number: {doc.gst_no}. Example: '27ABCDE1234F1Z5' (2 digits for state, PAN format, 3-digit suffix)")

# required_documents = ["MSME Certificate", "Cancel Cheque", "Pan Card"]

# # Ensure document_attachment is not None before iterating
# if not doc.document_attachment:
#     frappe.throw("Please attach the required documents.")

# # Check if all required documents are attached and have valid attachments
# attached_documents = set()  # To store names of documents with valid attachments

# for doc_attachment in doc.document_attachment:
#     # Check if the `documents` field is empty for any row
#     if not doc_attachment.documents:
#         frappe.throw(f"Please attach the document for '{doc_attachment.name1}' in the document attachment table.")

#     # Check if the document is one of the required documents
#     if doc_attachment.name1 in required_documents:
#         attached_documents.add(doc_attachment.name1)

# # Check if all required documents are present
# missing_documents = [doc for doc in required_documents if doc not in attached_documents]
# if missing_documents:
#     frappe.throw(f"Please attach the required documents: {', '.join(missing_documents)}")



import re
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
        if self.msme_no:
            # Regex pattern to validate MSME number (Udyam-<StateCode>-<12-Digits>)
            msme_pattern = r"^UDYAM-[A-Z]{2}-\d{12}$"

            # Check if MSME number matches the pattern
            if not re.match(msme_pattern, self.msme_no):
                frappe.throw(f"Invalid MSME Number: {self.msme_no}. Example: 'UDYAM-DL-123456789012'")

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








# import frappe
import requests

@frappe.whitelist()
def get_gst_details(gst_no):  # Use gst_no instead of doc.gst_no
    url = f"https://gsp.adaequare.com/test/enriched/ewb/master/GetGSTINDetails?GSTIN={gst_no}"
    
    headers = {
        'x-rapidapi-host': 'gst-return-status.p.rapidapi.com',
        'x-rapidapi-key': '60cd4c7bcdmshdcf4ab58e1d3aa7p100239jsn88cb5c60cde3',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Ensure successful response
        return response.json()  # Send response data back
    except requests.exceptions.RequestException as e:
        frappe.throw(f"API Request Failed: {str(e)}")
