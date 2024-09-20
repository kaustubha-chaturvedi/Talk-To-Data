from fastapi import FastAPI, HTTPException, Form
from db_utils import load_db, load_csv, get_query_history, store_query
from query_chain import infer

app = FastAPI()

@app.post("/query")
def run_query(data_uri: str = Form(...), question: str = Form(...)):
    try:
        # Infer data type from the data_uri (e.g., if it ends with '.csv', treat as CSV)
        if data_uri.endswith('.csv'):
            db = load_csv(data_uri)  # Load CSV data
        else:
            db = load_db(data_uri)   # Load SQL database

        answer = infer(db, question, is_csv=data_uri.endswith('.csv'))
        
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
