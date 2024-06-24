# Copyright (c) 2023, Crisco Consulting and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeAllocationLog(Document):
	pass


@frappe.whitelist()
def check_resource_availability(employee):
    emp_allocation_log = frappe.db.get_all("Employee Allocation Log",{"employee":employee,'status':'Allocated'},["name","from_date","to_date","project","employee"])
    if emp_allocation_log:
        message= emp_allocation_log
        return frappe._dict({"status":True,"message":message})
    else:
        return frappe._dict({"status":False,"message":"No Projects Allocated"})
