import requests
import json

url = "https://api.easi.utoronto.ca/ttb/getPageableCourses"


def fetch(course_title, sessions):
    session_list = []
    if sessions == "f":
        session_list = ["20239"]
    elif sessions == "s":
        session_list = ["20241"]
    else:
        session_list = [
            "20239",
            "20241",
            "20239-20241"
        ]

    payload = json.dumps({
        "courseCodeAndTitleProps": {
            "courseCode": "",
            "courseTitle": course_title,
            "courseSectionCode": "",
            "searchCourseDescription": True
        },
        "departmentProps": [],
        "campuses": [],
        "sessions": session_list,
        "requirementProps": [],
        "instructor": "",
        "courseLevels": [],
        "deliveryModes": [],
        "dayPreferences": [],
        "timePreferences": [],
        "divisions": [
            "ARTSC"
        ],
        "creditWeights": [],
        "page": 1,
        "pageSize": 20,
        "direction": "asc"
    })
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://ttb.utoronto.ca',
        'Referer': 'https://ttb.utoronto.ca/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text
