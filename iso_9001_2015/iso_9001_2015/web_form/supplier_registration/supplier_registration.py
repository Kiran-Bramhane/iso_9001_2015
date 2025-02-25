import frappe
import requests
import frappe
import uuid

def get_context(context):
	# do your magic here
	pass

@frappe.whitelist()
# def fetch_token():

def fetch_gst_data(gst_no):
    length = 8
    random_string = str(uuid.uuid4()).replace('-', '')[:length]
    url = f"https://gsp.adaequare.com/test/enriched/ewb/master/GetGSTINDetails?GSTIN={gst_no}"  # Replace with actual GST API
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJnc3AiXSwiZXhwIjoxNzQyMjA3NDg2LCJhdXRob3JpdGllcyI6WyJST0xFX1NCX0FQSV9UQVhfQ0FMQ1VMQVRJT04iLCJST0xFX1NCX0FQSV9HU1RfQ09NTU9OIiwiUk9MRV9TQl9FX0FQSV9HU1RfUkVUVVJOUyIsIlJPTEVfU0JfQVBJX0dTVF9SRVRVUk5TIiwiUk9MRV9TQl9BUElfRVdCIiwiUk9MRV9TQl9FX0FQSV9FV0IiLCJST0xFX1NCX0VfQVBJX0dTVF9DT01NT04iLCJST0xFX1NCX0FQSV9FSSIsIlJPTEVfU0JfRV9BUElfRUkiLCJST0xFX1NCX0FQSV9HU1BfT1RIRVJTIl0sImp0aSI6IjVhMzY3OTgyLTRlZjAtNGYwMC05MzI1LWMwZWVmNTMzNThiNyIsImNsaWVudF9pZCI6IkVERjZFMkExMjdFNTQyQkVBMzk3MjVCODQ1MkZEMUM0In0.-Rpo8KLdTSpSN-2BuyLBd_efkwFjLxSaIyJny5t3vt0",
               "Content-Type": "application/json",
               "username": "05AAACG2115R1ZN",
               "password": "abc123@@",
               "gstin": "05AAACG2115R1ZN",
               "requestid":random_string
               }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Invalid GST Number"}
