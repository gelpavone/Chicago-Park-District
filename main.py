import requests
import json

ROOT = "https://anc.apm.activecommunities.com/chicagoparkdistrict/rest"

# obligatory post body; just copied from what the browser sends. (the req breaks without it.)
payload = {
    "activity_search_pattern": {
        "skills": [],
        "time_after_str": "",
        "days_of_week": None,
        "activity_select_param": 2,
        "center_ids": [],
        "time_before_str": "",
        "open_spots": None,
        "activity_id": None,
        "activity_category_ids": [],
        "date_before": "",
        "min_age": None,
        "date_after": "",
        "activity_type_ids": [],
        "site_ids": [],
        "for_map": False,
        "geographic_area_ids": [],
        "season_ids": [],
        "activity_department_ids": [],
        "activity_other_category_ids": [],
        "child_season_ids": [],
        "activity_keyword": "",
        "instructor_ids": [],
        "max_age": None,
        "custom_price_from": "",
        "custom_price_to": "",
    },
    "activity_transfer_pattern": {},
}

# pagination is controlled by this silly header
page_info_header = {"order_by": "Name", "page_number": 1, "total_records_per_page": 10}

# turn the header to json
headers = {
    "content-type": "application/json",
    "page_info": json.dumps(page_info_header),
}

activity_list_url = f"{ROOT}/activities/list"
response = requests.post(activity_list_url, json=payload, headers=headers)
data = response.json()
items: list[dict] = data["body"]["activity_items"]

for activity in items:
    summary = {}

    activity_id = activity["id"]
    activity_detail_url = f"{ROOT}/activity/detail/{activity_id}"
    activity_response = requests.get(activity_detail_url)
    activity_detail_data: dict = activity_response.json()["body"]["detail"]

    summary["name"] = activity_detail_data["activity_name"]
    summary["date_range"] = [
        activity_detail_data["first_date"],
        activity_detail_data["last_date"],
    ]

    facilities: list[dict] = activity_detail_data["facilities"]
    # loop over each facility and request.get() each one's details

    summary["facility_info"] = []
    for facility in facilities:
        facility_id = facility["id"]
        facility_detail_url = f"{ROOT}/reservation/resource/simple/detail/{facility_id}"
        facility_response = requests.get(facility_detail_url)
        facility_data: dict = facility_response.json()["body"]["resource_detail"][
            "general_information"
        ]

        normalized_address = f"{facility_data['address1']}, {facility_data['city']}, {facility_data['state']} {facility_data['zip_code']}"
        summary["facility_info"].append(
            {
                "name": facility_data["facility_name"],
                "address": normalized_address,
            }
        )

    print(json.dumps(summary, indent=2))
