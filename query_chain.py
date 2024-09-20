import re,os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser

MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def chain_create(db):
    llm = ChatGroq(model=MODEL, api_key=GROQ_API_KEY)
    chain = create_sql_query_chain(llm, db)
    return chain

def clean_sql_query(sql_query):
    sql_query = sql_query.replace("\\_", "_").replace("\\\"", "\"")
    
    sql_query = re.sub(r'(\w)(JOIN|FROM|GROUP BY|ORDER BY|LIMIT)', r'\1 \2', sql_query)
    sql_query = re.sub(r'(COUNT|SELECT|WHERE|AND|OR|ON)(\w)', r'\1 \2', sql_query)

    sql_query = re.sub(r'\s+', ' ', sql_query).strip()
    sql_query = sql_query.replace("OR DER BY", "ORDER BY")
    return sql_query

def sql_infer(db, chain, user_question):
    print(MODEL)
    sql_query = chain.invoke({"question": user_question})

    cleaned_query = clean_sql_query(sql_query)

    try:
        result = db.run(cleaned_query)
    except Exception as e:
        print(f"Error running the query: {cleaned_query}")
        raise e

    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, generate a proper reply to give to user.

        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
    )

    llm_model = ChatGroq(model=MODEL, api_key=GROQ_API_KEY)
    chain = answer_prompt | llm_model | StrOutputParser()
    ans = chain.invoke({"question": user_question, "query": cleaned_query, "result": result})
    return {"text": ans, "sql_query": cleaned_query, "result": result}

