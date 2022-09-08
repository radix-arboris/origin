#!/usr/bin/python

#!/usr/bin/python3
import os
line_num = 1
inputdir = "/DriveArchive2/origin/data"
for filename in os.listdir(inputdir):
    print(filename)
    with open(inputdir+"/"+filename) as f:
        data = f.readlines()[line_num]
        new_data = data.replace("_", " ")
        print(new_data)
        updata = new_data.title()
        finaldata = updata[0].lower() + updata[1:]
        f.close()
        lines = open(inputdir+"/"+filename, 'r').readlines()
        lines[line_num] = finaldata
        out = open(inputdir+"/"+filename, 'w')
        out.writelines(lines)
        out.close()