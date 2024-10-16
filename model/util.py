import re
import requests
import pandas as pd
import uuid
import json
import numpy as np
from datetime import datetime
from typing import List, Tuple

def text_validation(text: str) -> bool:
    rule = r'^(\d+)(,\s\d+)*$'
    return bool(re.match(rule, text))

def date_validation(start_date: datetime, end_date: datetime) -> bool:
    if start_date > end_date:
        return False
    else:
        return True

def text_formatting(text: str) -> list:
    text_list = text.split(", ")
    return text_list

def make_request(text: str):
    response = requests.get(f"http://fabtec.ifc-riodosul.edu.br/issues.json?issue_id={text}&key=b7c238adc2c0af943c1f0fa9de6489ce190bd6d5&status_id=*")
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code

def create_sprint(name: str, start_date: datetime, end_date: datetime, text_list: List[str]) -> bool:
    verification = True
    sprint = pd.DataFrame({"id":[], "subject":[], "created_on":[], "closed_on":[]})

    for text in text_list:
        response = make_request(text)
        if type(response) != int:
            id = response["issues"][0]["id"]
            subject = response["issues"][0]["subject"]
            created_on = response["issues"][0]["created_on"][:10]
            closed_on = response["issues"][0]["closed_on"][:10]

        if datetime.strptime(created_on, "%Y-%m-%d").date() >= start_date and datetime.strptime(closed_on, "%Y-%m-%d").date() <= end_date:
            sprint.loc[len(sprint)] = {"id":id, "subject":subject, "created_on":created_on, "closed_on":closed_on}
            print("teste")
        else:
            verification = False
            break
    
    if verification:
        sprint.attrs["name"] = name
        sprint.attrs["start_date"] = str(start_date)
        sprint.attrs["end_date"] = str(end_date)

        save_sprint = {
            "data": sprint.to_dict(orient='split'),
            "metadata": sprint.attrs
        }
        with open(f"sprint/{uuid.uuid4()}.json", "w") as file:
            json.dump(save_sprint, file)

        return True
    else:
        return False

def read_sprint(path_file: str) -> pd.DataFrame:
    with open(path_file, "r") as file:
        read_sprint = json.load(file)
    
    sprint = pd.DataFrame(**read_sprint["data"])
    sprint.attrs = read_sprint["metadata"]

    return sprint

def difference_between_date(start_date: str, end_date: str) -> int:
    working_days = np.busday_count(start_date, end_date)
    return working_days

def linear_distribute_tasks(dataframe: pd.DataFrame, working_days: int) -> Tuple[List[int], List[int]]:
    list_days = list(range(0, working_days + 1))
    total_number_tasks = len(dataframe)
    list_tasks = []

    tasks_per_day = total_number_tasks // working_days
    extra_tasks = total_number_tasks % working_days
    remaining_tasks = total_number_tasks
    list_tasks.append(total_number_tasks)

    for index in range(working_days):
        if extra_tasks > 0:
            extra_tasks -= 1
            remaining_tasks -= (tasks_per_day + 1)
        else:
            remaining_tasks -= tasks_per_day
        list_tasks.append(int(remaining_tasks))

    return list_days, list_tasks

def not_linear_distribute_tasks(dataframe: pd.DataFrame, working_days: int, start_date: str):
     
    list_days = list(range(0, working_days + 1))
    list_tasks = list([0] * (working_days + 1))
    tasks = dataframe.groupby("closed_on").size().reset_index(name="tasks_count")

    tasks["difference"] = tasks["closed_on"].apply(
        lambda x: difference_between_date(start_date, x)
    )

    total_number_tasks = tasks["tasks_count"].values.sum()
    list_tasks[0] = int(total_number_tasks)

    for index in range(1, working_days):
        if index in tasks["difference"].values:
            tasks_per_day = tasks.loc[tasks["difference"] == index, "tasks_count"].values[0]
            total_number_tasks = total_number_tasks - tasks_per_day
        list_tasks[index] = int(total_number_tasks)

    return list_days, list_tasks