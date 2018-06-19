import parso
from parso.python.tokenize import tokenize
from parso.python.token import tok_name
import json
import sys 

file = open(sys.argv[1],'r')
file_content = file.read()

tokens = []

for token in tokenize(file_content, version_info=(3,6)):
	tmp = dict()
	tmp["line"]=(token.start_pos)[0];
	tmp["char"]=((token.start_pos)[1])+1;
	tmp["type"]=str(tok_name[token.type])
	tmp["value"]=str(token.string)
	tokens.append(tmp)

print ("here")
print ( json.dumps(tokens, indent=4, sort_keys=True) )

#with open("output.json", "w") as f:
#    json.dump(tokens, f, indent = 4, sort_keys = True)
	

