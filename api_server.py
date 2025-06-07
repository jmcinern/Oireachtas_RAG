import importlib.machinery
import importlib.util
from fastapi import FastAPI
from pydantic import BaseModel

# Dynamically load the existing streamlit script as a module
loader = importlib.machinery.SourceFileLoader('dail_app', 'd\u00e1il_app.py')
spec = importlib.util.spec_from_loader(loader.name, loader)
dail_app = importlib.util.module_from_spec(spec)
loader.exec_module(dail_app)

app = FastAPI()

class Query(BaseModel):
    speaker: str
    topic: str

@app.post('/generate')
def generate(query: Query):
    answer = dail_app.generate_answer(query.speaker, query.topic, dail_app.SPEAKERS)
    return {'answer': answer}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
