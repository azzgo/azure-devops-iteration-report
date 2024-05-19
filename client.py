import httpx
import streamlit as st
import os
import base64

AZURE_TOKEN = os.environ.get('AZURE_TOKEN')
AZURE_PROJECT = os.environ.get('AZURE_PROJECT')
AZURE_ORG = os.environ.get('AZURE_ORG')
AZURE_TEAM = os.environ.get('AZURE_TEAM')
AZURE_BOARD_ID = os.environ.get('AZURE_BOARD_ID')

if not AZURE_TOKEN or not AZURE_PROJECT or not AZURE_ORG or not AZURE_TEAM:
    raise Exception("Missing environment variables")

username = ""
password = AZURE_TOKEN
userpass = username + ":" + password
b64 = base64.b64encode(userpass.encode()).decode().strip()

headers = {"Authorization": "Basic %s" %
           b64, 'Content-Type': 'application/json'}

client = httpx.Client(
    base_url="https://dev.azure.com",
    headers=headers
)


# no use yet
def get_iteration_list():
    r = client.get(
        f'/{AZURE_ORG}/{AZURE_PROJECT}/{AZURE_TEAM}/_apis/work/teamsettings/iterations'
    )
    if (r.status_code != 200):
        raise Exception(r.text)
    return r.json()

def get_current_iterations():
    r = client.get(
        f'/{AZURE_ORG}/{AZURE_PROJECT}/{AZURE_TEAM}/_apis/work/teamsettings/iterations?$timeframe=current'
    )
    if (r.status_code != 200):
        raise Exception(r.text)
    return r.json().get('value') or []


# no use yet
def get_board_info(iterationPath: str):
    # POST https://dev.azure.com/{organization}/{project}/{team}/_apis/wit/wiql?api-version=7.2-preview.2
    work_items_response = client.post(f'{AZURE_ORG}/{AZURE_PROJECT}/{AZURE_TEAM}/_apis/wit/wiql?api-version=7.2-preview.2', json={
        'query': f"SELECT [System.Id],[System.WorkItemType],[System.Title],[System.Tags],[System.BoardColumn],[Microsoft.VSTS.Scheduling.StoryPoints] FROM WorkItems WHERE [System.TeamProject] = @project AND [System.WorkItemType] = 'User Story' AND [System.IterationPath] = '{iterationPath}'"
    })
    if (work_items_response.status_code != 200):
        raise Exception(work_items_response.text)
    work_items_json = work_items_response.json()
    work_items = work_items_json['workItems']
    columns = work_items_json['columns']

    work_item_batch_details_info_response = client.post(f'/{AZURE_ORG}/{AZURE_PROJECT}/_apis/wit/workitemsbatch?api-version=7.2-preview.1', json={
        'ids': [work_item['id'] for work_item in work_items],
        'fields': [column['referenceName'] for column in columns]
    })

    work_detail_items = work_item_batch_details_info_response.json().get('value')
    return {
        'columns': columns,
        'work_items': work_detail_items
    }

@st.cache_data(ttl='5m')
def get_iteration_odata():
    # right value is now()
    # for debug at any date such as
    # 2024-04-07
    r = client.get(f'https://analytics.dev.azure.com/{AZURE_ORG}/{AZURE_PROJECT}/_odata/v3.0-preview/WorkItemBoardSnapshot', params={
        '$apply': '''filter(
            WorkItemType eq 'User Story' 
            and ColumnName ne 'Ready for Iteration'
            and DateValue ge Iteration/StartDate
            and DateValue le Iteration/EndDate
            and Iteration/StartDate le now() 
            and Iteration/EndDate ge now()
        )
        /groupby(
            (DateValue,ColumnName,WorkItemType,Area/AreaPath,Iteration/IterationPath,Iteration/StartDate,Iteration/EndDate),
            aggregate($count as Count, StoryPoints with sum as TotalStoryPoints)
        )'''})
    if (r.status_code != 200):
        raise Exception(r.text)
    return r.json().get('value') or []

