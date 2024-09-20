from fastapi import FastAPI, HTTPException, Form
from db_utils import load_db, get_query_history, store_query
from query_chain import chain_create, sql_infer

app = FastAPI()

@app.post("/query")
def run_query(db_uri: str = Form(...), question: str = Form(...)):
    try:
        db = load_db(db_uri)
        chain = chain_create(db)
        answer = sql_infer(db, chain, question)
        store_query(question, answer["sql_query"], str(answer["result"]))
        return {"answer": answer["text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history():
    histories = get_query_history()
    
    response = {
        "count": len(histories),
        "history": dict((idx, {"question": q, "query": query, "result": result}) for idx, q, query, result in histories)   
    }

    return response