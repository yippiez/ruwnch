
# Watch this file and see test.txt changing live.
#
# FOR WINDOWS
# python ruwnch.py .example\test.py "python .example\test.py"
#
# FOR LINUX
# python3 ruwnch.py .example/test.py "python .example/test.py"
#

with open("test.txt", "w") as f:
    f.write("Hello World!")
