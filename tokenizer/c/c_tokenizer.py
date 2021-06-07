import clang.cindex
import json
import sys
import shutil
import tempfile
import os


# apparently, the file name must end in .cpp (or some standard
# c/c++ suffix to be successfully tokenized)

# make a temprary filename
tmp_cpp_file_handle,tmp_cpp_file_name=tempfile.mkstemp(suffix=".cpp")
# copy the concatenated file to the temporary file location
shutil.copy(sys.argv[1],tmp_cpp_file_name)

if (os.path.isfile("/usr/lib/llvm-6.0/lib/libclang.so.1")):
        clang.cindex.Config.set_library_file("/usr/lib/llvm-6.0/lib/libclang.so.1")
elif (os.path.isfile("/usr/lib/llvm-3.8/lib/libclang-3.8.so.1")):
        clang.cindex.Config.set_library_file("/usr/lib/llvm-3.8/lib/libclang-3.8.so.1")
idx = clang.cindex.Index.create()

# parse the input file
parsed_data = idx.parse(tmp_cpp_file_name)

# remove the temporary file
os.remove(tmp_cpp_file_name)

tokens = []

for token in parsed_data.get_tokens(extent = parsed_data.cursor.extent):
	tmp = dict()
	tmp["line"]=int(token.location.line)
	tmp["char"]=int(token.location.column)
	tmp["type"]=(str(token.kind))[10:]
	tmp["value"]=str(token.spelling)
	tokens.append(tmp)

print ( json.dumps(tokens, indent=4, sort_keys=True) )
