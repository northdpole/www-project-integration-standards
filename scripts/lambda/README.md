AWS Serverless Function to filter CREs via REST requests
===

Supported methods:
---

Get specific cre by id
` curl "https://<endpoint>/cre/011-040-026"`

Get all CREs that mention the link and tag,
`curl "https://<endpoint>/link?tag=<tag>&val=<tag>"`

Get all cres known to the REST API
`curl https://<endpoint>/cres`


Contributing
---

Deploy locally:

`sam build && sam local start-api`

Deploy on AWS:
(you might need to creat Roles etc yourself if you find a way to make this generic I'll buy you a beer)
` sam build && sam deploy`

