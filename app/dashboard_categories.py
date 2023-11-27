searching_categories = [
    {
        "id": 1,
        "name": "Tra cứu bệnh nhân",
        "active_page": "list_patients",
        "endpoint": "patient.list_patients",
    },
    {
        "id": 2,
        "name": "Tra cứu thuốc",
        "active_page": "list_medicines",
        "endpoint": "medicine.list_medicines",
    },
]

dashboard_categories = {
    "Nurse": [],
    "Doctor": [],
    "Cashier": [],
    "Admin": [],
    "Patient": [],
    "Unknown": [],
}

dashboard_categories["Doctor"].extend(searching_categories)
dashboard_categories["Nurse"].extend(searching_categories)
