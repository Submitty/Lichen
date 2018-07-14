import javac_parser
import json
import sys 

java= javac_parser.Java()

file = open(sys.argv[1],'r')
file_content = file.read()

tokens = []

for token in java.lex(file_content):
	tmp = dict()
	tmp["line"]=token[2][0]
	tmp["char"]=token[2][1]+1
	tmp["type"]=str(token[0])
	tmp["value"]=str(token[1])
	tokens.append(tmp)

tokens.pop()
print ( json.dumps(tokens, indent=4, sort_keys=True) )