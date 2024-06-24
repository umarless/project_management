import frappe

def create_emp_allocation_log(doc,method=None):
	if doc.employee_allocation_details:
		for row in doc.employee_allocation_details:
			if frappe.db.exists("Employee Allocation Log",{'employee':row.employee}):
				ead_doc = frappe.get_doc("Employee Allocation Log",{'employee':row.employee})
				ead_doc.from_date = row.from_date
				ead_doc.to_date = row.to_date
				ead_doc.status = row.status
			else:
				ead = frappe.new_doc("Employee Allocation Log")
				ead.employee = row.employee
				ead.from_date = row.from_date
				ead.to_date = row.to_date
				ead.project = doc.name
				ead.status = row.status
				ead.allocation_date = frappe.utils.nowdate()
				ead.insert()
				frappe.msgprint("Employee Allocated to this project!!")

def get_emp_allocation_log(employee,project):
	bin = frappe.db.get_value("Employee Allocation Log", {"employee": employee, "project": project})
	if not bin:
		bin_obj = _create_log(employee,project)
	else:
		bin_obj = frappe.get_doc("Employee Allocation Log", bin, for_update=True)
	bin_obj.flags.ignore_permissions = True
	return bin_obj

def _create_log(employee, project):
	"""Create a log and take care of concurrent inserts."""

	log_creation_savepoint = "create_allocation_log"
	try:
		frappe.db.savepoint(log_creation_savepoint)
		bin_obj = frappe.get_doc(doctype="Employee Allocation Log", employee=employee, project=project)
		bin_obj.flags.ignore_permissions = 1
		bin_obj.insert()
		frappe.msgprint("Employee Allocated to this project!!")
	except frappe.UniqueValidationError:
		frappe.db.rollback(save_point=log_creation_savepoint)  # preserve transaction in postgres
		bin_obj = frappe.get_last_doc("Employee Allocation Log", {"employee": employee, "project": project})

	return bin_obj

def get_or_make_employee_allocation_log(employee: str, project: str) -> str:
	bin_record = frappe.db.get_value("Employee Allocation Log", {"employee": employee, "project": project})

	if not bin_record:
		bin_obj = _create_log(employee, project)
		bin_record = bin_obj.name
	return bin_record

def update_log(doc,method=None):
	# update bin for each warehouse
	for row in doc.employee_allocation_details:
		bin_name = get_or_make_employee_allocation_log(row.employee, doc.name)

		updated_values = {"from_date": row.from_date, "to_date": row.to_date, "status":row.status}
		frappe.db.set_value("Employee Allocation Log", bin_name, updated_values, update_modified=True)
