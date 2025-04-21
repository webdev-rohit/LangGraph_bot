# importing internal modules
from utils import llm
from prompts import classify_incidents_prompt
from create_vectorstore import Chroma, OpenAIEmbeddings

# importing other important libraries
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Connecting with SNOW instance
url = os.getenv('SNOW_INSTANCE_URL')
username = os.getenv('SNOW_USERNAME')
password = os.getenv('SNOW_PASSWORD')
incident_table_url = os.getenv('SNOW_INCIDENT_TABLE_URL')

# importing tool library
from langchain_community.tools import tool

headers = {"Content-Type": "application/json", "Accept": "application/json"}

# Note - LLM understands the purpose of the tool from the defined docstring in the tool function. So, it is compulsory to define a docstring in the tool function as shown below
# Defining incident status checking tool.
@tool
def check_snow_incident_status(inc_number):
    """This tool checks the status of the ticket provided an incident ticket number. If the ticket number is not provided then the llm needs to ask about the ticket number. Example of an incident ticket number - INC0010018. So, the ticket number will always start with 'inc' or 'INC' followed by 7 numerical digits. If that is not the case then the llm must ask for a valid ticket number. This tool MUST BE USED ONLY WHEN USER REQUESTS TO KNOW THE STATUS OF A TICKET and not for any general queries."""

    incident_states = {1:"New",2:"In Progress",3:"On Hold",6:"Resolved",7:"Closed",8:"Canceled"}
    status_url = incident_table_url+'?number='+inc_number
    response = requests.get(url=status_url, auth=(username,password))
    if response.status_code == 200 or response.status_code == 201:
        status_num = int(response.json()['result'][0]['state'])
        status = incident_states[status_num]
        print('\nstatus >', status)
        return f"The status of the ticket - {inc_number} is {status}"
    else:
        print('\nSome error occurred while fetching status of ticket >', response.text)
        return 'Some error occured during fetching status of ticket'

# Defining incident creation tool
@tool
def create_snow_incident(user_issue, caller):
    """This tool creates an incident ticket provided fields like the user issue and caller name. However, the tool needs to first check if there is already a relevant solution present in its vectorstore, if this case is False only then it has to proceed for ticket creation. Nevertheless, the bot has to ask the user if still he/she wants to create the ticket because the solution provided might not be sometimes sufficient for the user.
    Steps to follow -
    1) First check if user has provided a name and description of their issue.
    2) Secondly, check if there is a relevant solution for the issue in the vectorstore. If yes, give the solution and ask if user is still unstatisfied with the solution then ticket creation to be done.
    3) If there is no relevant solution present in the vectorstore then simply create the ticket . 
    Note - If the user hasn't mentioned the issue itself and has just asked for ticket creation the llm is supposed to ask the user for the issue. This tool MUST BE USED ONLY WHEN USER WANTS TO CREATE A TICKET and not for any general queries."""

    print('\ncaller name >', caller)
    # decide if caller name exists in the callers list in SNOW -
    callersList = fetch_users_list()
    print('\nexisting callersList >', callersList)
    if caller in callersList:
        # first check if there already exists a relevant solution from the vectorstore
        vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=OpenAIEmbeddings()
        )
        results = vectorstore.similarity_search_with_score(user_issue, k=1)
        print('similar documents >', results)

        if results and results[0][1] >= 0.6:
            doc = results[0][0]
            return f"Found a relevant solution: {doc.page_content}"
        else:
            # determine urgency by calling LLM
            result = llm.invoke(classify_incidents_prompt+" "+user_issue)
            print('\nurgency decided by LLM >', result.content)

            urgency_dict = {'High':1, 'Medium':2, 'Low':3}
            payload = {
                "short_description": user_issue,
                "caller_id": caller,
                "state": 1,  # New
                "urgency": urgency_dict[result.content]
            }

            response = requests.post(url=incident_table_url, auth=(username, password), headers=headers ,json=payload)
            if response.status_code == 200 or response.status_code == 201:
                inc_number = response.json()['result']['number']
                print(f'\nIncident {inc_number} created successfully')
                # print(response.json())
                return f'Incident {inc_number} created successfully having urgency - {urgency_dict[result.content]}'
            else:
                print('\nSome error occurred during incident ticket creation >', response.text)
                return 'Some error occured during incident ticket creation'
    else:
        print('\nYou do not seem to be in our caller list for creating tickets, so we cannot create the ticket for you. Please specify a valid user name')
        return 'You do not seem to be in our caller list for creating tickets, so we cannot create the ticket for you. Please specify a valid user name'

def fetch_users_list():
    params = {
        'sysparm_fields': 'caller_id.name',
        'sysparm_limit': '100',
    }
    response = requests.get(incident_table_url, auth=(username, password), headers=headers, params=params)
    data = response.json()
    names = sorted(data['result'], key=lambda x:x['caller_id.name'])

    names = [name['caller_id.name'] for name in names]
    userNames = list(set(names))
    for name in userNames:
        if name == '':
            userNames.remove(name)
    # print(userNames, len(userNames))
    return userNames

tools = [check_snow_incident_status, create_snow_incident]