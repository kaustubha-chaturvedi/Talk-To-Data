from fastapi import FastAPI, HTTPException, Form
from db_utils import load_db
from query_chain import chain_create, sql_infer

app = FastAPI()

@app.post("/query")
def run_query(db_uri: str = Form(...), question: str = Form(...)):
    try:
        db = load_db(db_uri)
        chain = chain_create(db)
        answer = sql_infer(db, chain, question)
        return {"answer": answer["text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))