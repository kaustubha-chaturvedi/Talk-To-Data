import re
import os
from pandasql import sqldf
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser

MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def chain_create(db):
    llm = ChatGroq(model=MODEL, api_key=GROQ_API_KEY)
    chain = create_sql_query_chain(llm, db)
    return chain

def csv_prompt():
    # Use LLM to convert natural language to pandas query
    template = """You are a powerful text-to-SQL model. Your job is to answer questions about a database. You are given a question and context regarding one or more tables. Dont add \n characters.
        Do not include "SELECT short\_name, long\_name" this type of queries which have backslash in them.
        You must output the SQL query that answers the question in a single line.

        ### Input:
        `{question}`

        ### Context:
        `{context}`

        ### Response:
        """

    prompt = ChatPromptTemplate.from_template(template)
    return prompt

def clean_sql_query(sql_query):
    sql_query = sql_query.replace("\\_", "_").replace("\\\"", "\"")
    
    sql_query = re.sub(r'(\w)(JOIN|FROM|GROUP BY|ORDER BY|LIMIT)', r'\1 \2', sql_query)
    sql_query = re.sub(r'(COUNT|SELECT|WHERE|AND|OR|ON)(\w)', r'\1 \2', sql_query)

    sql_query = re.sub(r'\s+', ' ', sql_query).strip()
    sql_query = sql_query.replace("OR DER BY", "ORDER BY")
    return sql_query

def infer(db, user_question, is_csv=False):

    if is_csv:
        # Load the CSV file
        df, context = db
        prompt = csv_prompt()
        llm = ChatGroq(model=MODEL, api_key=GROQ_API_KEY)
        chain = prompt | llm
        response = chain.invoke({"question": user_question, "context": context}).content
        final = response.replace("`", "").replace("sql", "").strip()
        print(response, final)
        result = sqldf(final, locals())

        return {
            "text": f"Query Results: {result.to_dict()}",
            "sql_query": final,
            "result": result.to_dict()
        }

    else:
        # Handle SQL database
        chain = chain_create(db)
        sql_query = chain.invoke({"question": user_question})
        cleaned_query = clean_sql_query(sql_query)

        try:
            result = db.run(cleaned_query)
        except Exception as e:
            print(f"Error running the SQL query: {cleaned_query}")
            raise e

        return {
            "text": f"Query Results: {result}",
            "sql_query": cleaned_query,
            "result": result
        }
