# -*- coding: utf-8 -*-
"""
dependency: pip install flask_restful

Based on example in https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3

Running on http://127.0.0.1:5000/

[anick@sarpedon code]$ curl http://localhost:5000/twq/"b"

curl  http://sarpedon.cs.brandeis.edu/twq/a

"""

from flask import Flask
from flask_restful import Api, Resource, reqparse
import pdb

import tw_query

app = Flask(__name__)
api = Api(app)

d_query2result = { "a" : "letter a",
                   "b" : "letter b"
                   }

class TwQuery(Resource):
    def get(self, query):
        try:
            #pdb.set_trace()
            #result = [d_query2result[query], d_query2result]
            #return result, 200
            result = tw_query.fquery(query)
            return(result)
        except:
            return "Query could not be processed", 404
 
#api.add_resource(TwQuery, "/twq/<string:query>")
api.add_resource(TwQuery, "/twq/<string:query>")

if __name__ == "__main__":
    app.run(debug=True)

