# Text-to-SQL Query System with Multi-Source Data

Unlike previous one [DB-Engineer](https://github.com/kaustubha-chaturvedi/DB-Engineer) this one can really connect to db and instead of providing frontend it provides FastAPI backend to communicate with db

## How to use

To the the program
```shell
uvicorn main:app --reload
```

Send post request to `/query` with body params

`data_uri` uri of sql connection or csv file
`question` natural langauge question