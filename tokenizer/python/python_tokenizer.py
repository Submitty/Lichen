from parso.python.tokenize import tokenize
import json
import sys

file = open(sys.argv[1], 'r')
file_content = file.read()

tokens = []

for token in tokenize(file_content, version_info=(3, 6)):
    if (str(token.string) != ""):
        tmp = dict()
        tmp["line"] = (token.start_pos)[0]
        tmp["char"] = ((token.start_pos)[1]) + 1
        tmp["type"] = ((str(token.type))[17:]).strip(")")
        if tmp["type"] == "OP":
            tmp["type"] += "-" + str(token.string)
        tmp["value"] = str(token.string)
        tokens.append(tmp)

print(json.dumps(tokens, indent=4, sort_keys=True))
