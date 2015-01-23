'''
Created on 22 Jan 2015

@author: Chad
'''
import wiconnectpy
import sys
import random
import time
cmd_list = [["ls"], ["scan"], ["ping -g"], ["file_open test_file.txt", "read 0 1000", "close all"], ["gpio_dir 10 out", "gpio_set 10 0", "gpio_set 10 1"], ["get gp u"]]

a = wiconnectpy.wiconnectpy(sys.argv[1])
print "Testing...\n"
i = 0
ecount = 0
while 1:
    f = open("test.log", "a")
    sys.stdout.write("\rCount:{}\tErorrs:{}".format(i,ecount))
    cmd = cmd_list[random.randint(0, len(cmd_list)-1)]
    for cmd_step in cmd:
        f.write("%%%%%%% {}\n".format(cmd_step))
        r = a(cmd_step)
        f.write(r)
        f.write("\n")
        
        if r == "":
            ecount = ecount + 1
            f.write("%%%%%%% ERROR or not responce\n")
        else:            
            i = i + 1
    time.sleep(random.randint(0, 500)/100)
    f.close()
        
 
