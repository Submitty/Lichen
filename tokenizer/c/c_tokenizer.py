import clang.cindex
import json
import sys

clang.cindex.Config.set_library_file("/usr/lib/llvm-3.8/lib/libclang-3.8.so.1")
idx = clang.cindex.Index.create()

# parse the input file
parsed_data = idx.parse(sys.argv[1])

tokens = []

for token in parsed_data.get_tokens(extent = parsed_data.cursor.extent):
	tmp = dict()
	tmp["line"]=int(token.location.line)
	tmp["char"]=int(token.location.column)
	tmp["type"]=(str(token.kind))[10:]
	tmp["value"]=str(token.spelling)
	tokens.append(tmp)

with open("output.json", "w") as f:
    json.dump(tokens, f, indent = 4, sort_keys = True)
