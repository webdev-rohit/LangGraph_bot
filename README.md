# LangGraph based SNOW Ticket Assistant chatbot

## About LangGraph

Visit their official page -  https://www.langchain.com/langgraph

See the [documentation](https://langchain-ai.github.io/langgraph/) for understanding functionalities and features.

## About the Project

The Project is a demonstration of a tool based LLM Agent meant for the following 3 tasks-
1) Check the incident ticket status from Service-Now instance
2) Create an incident ticket in Service-Now and link it with JIRA board if urgency is high
3) Give answers for generic questions which are out of scope of the first two cases

## Watch the demo 📽️

Download the file - demo_video.webm provided in this repository to see the Streamlit demo.

## Architecture

Refer the file - Bot_flow.png provided in this repository.

## Code setup

To set up and run the project, follow these steps:

1. Clone the repository -
```bash
git clone https://github.com/webdev-rohit/LangGraph_bot.git
```

2. Virtual environment creation and activation in the project directory (Windows) -
```bash
python -m venv venv
cd <project_directory>/venv/Scripts
activate
```

3. Inside the activated virtual environment venv -
```bash
pip install -r requirements.txt
```

## Run the application locally

1. Run the API in a terminal -
```bash
python app.py
```

2. Run the Streamlit frontend in another terminal -
```bash
python -m streamlit run chat_app.py
```

Connect with me on my email - rohitvishssj5@gmail.com. Contributions are welcome!