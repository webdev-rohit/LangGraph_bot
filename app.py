## fastapi imports
from fastapi import FastAPI, HTTPException
import uvicorn

## internal module imports
from models import AskInput
from utils import answer_query

app = FastAPI(title="Demo LangGraph bot")

@app.get('/')
def home():
    try:
        return "Health check successful"
    except Exception as e:
        return "Error due to {e}"

@app.post('/ask')
def ask(request: AskInput):
    try:
        result = answer_query(request.user_query, request.session_id)
        return {'success':1, 'message': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__=="__main__":
    uvicorn.run(app=app, host='0.0.0.0', port=8080)