'''
Created on 15 Jan 2015

@author: Chad
'''
import sys
import requests
import json
import base64
import CRCUtil 



class default_cmd(object):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        
    def __call__(self, cmd_args="", data=""):
        print self.parent.send_cmd("{} {}".format(self.name, cmd_args), data)
 

class wiconnectpy(object):
    '''
    classdocs
    '''
    MAX_CHUNK_SIZE = 2500
    
    def __init__(self, addr, timeout=12, retries=1):
        '''
        Constructor
        '''
        self.timeout = timeout
        self.retries = retries
        self.data_buffer = ""
        self.url = "http://" + addr + "/command"
        
        self.create_helper_function()
        
    def __call__(self, cmd_string, data=""):
        cmd = cmd_string.split()[0]
        cmd_args = cmd_string.split()[1:]
        
        # Handle file_create data
        # file_create [-[e][u]] [-o] <filename> <size> [<version> [<type> [<crc>]]]
        if ((cmd == "fcr") or (cmd == "file_create")) and (cmd_string.find("-o") == -1):
            return self.send_fcr_cmd(cmd_args, data)
               
        # Handle stream_write data
        # stream_write <handle> <size> 
        elif (cmd == "write") or (cmd == "stream_write"):  
            return self.send_write_cmd(cmd_args[0], cmd_args[1], data)
        else:
            return self.send_cmd(cmd_string, data)             

    # Dynamically create functions
    def create_helper_function(self):
        funcs = self.send_cmd("help commands")
        if not funcs:
            return False
        funcs = funcs.replace(" ", "").split('\r\n')
        for func in funcs:
            #print func.split(":")
            full_func = func.split(":")[0]
            short_func = func.split(":")[1]
            setattr(self.__class__, full_func, default_cmd(self, full_func))
            
            if short_func != full_func:
                setattr(self.__class__, short_func, default_cmd(self, short_func))        
        
    def send_cmd(self, command, data=""):
        try:
            a = requests.post(self.url,  data=json.dumps({"command": base64.b64encode(command), "flags":0x7, "data": base64.b64encode(data)}), headers={"content-type":"application/json", "accepts":"application/json"})  
            if a.status_code == 200:
                return base64.b64decode(a.json()["response"]).rstrip()
            else:
                print "Error: {}".format(a.status_code), a.text

        except requests.exceptions.ConnectionError:
            print "Error connecting to {}".format(self.url)
            return ""
                       
    def send_write_cmd(self, stream_handle, size, data):
        
        # validate stream handle
        try:
            int(stream_handle)
        except:
            print "Invalid Stream handle: {}".format(stream_handle)
            return ""
        
        #Validate size
        try:
            if int(size) != len(data):
                print "Data size incorrect"
                return ""
        except:
            print "Data size wrong format"
            return ""
        
        # Send data in chunks to adhere to memory restrictions on module
        sys.stdout.write("Progress:   0%")
        init_size = float(len(data))
        while data:
            data_chunk = data[:self.MAX_CHUNK_SIZE]           
            resp = self.send_cmd("write {} {}".format(stream_handle, len(data_chunk)), data_chunk)
            if resp != "Success":
                return ""
            data = data[self.MAX_CHUNK_SIZE:]
            
            progress = (float(len(data)) / init_size) * 100
            sys.stdout.write("\rProgress: {:3d}%".format(100 - int(progress)))
         
        sys.stdout.write("\r                     \r")   
        return resp    
            
    def send_fcr_cmd(self, cmd_args, data):

        file_info = self.parse_fcr_args(cmd_args)
        if int(file_info["size"]) != len(data):
            print "Invalid file size"
            return ""
        
        crc = hex(CRCUtil.crc16(str(data)))
        if not file_info["crc"]:
            file_info["crc"] = crc
        elif str(crc) != file_info["crc"]:
            print "Invalid CRC"
            return ""

        # Reconstruct command string with updated arguments
        cmd_string = "fcr -o "
        if file_info["unprotect"] and file_info["essential"]:
            cmd_string += " -ue"
        else:
            if file_info["unprotect"]:
                cmd_string += " -u"
            elif  file_info["unprotect"]:
                cmd_string += " -e"
        if file_info["stream"]:
            cmd_string += " -o"
        
        cmd_string += " {} {} {} {} {}".format(file_info["name"], file_info["size"], file_info["version"], file_info["type"], file_info["crc"])
        print cmd_string

        stream_handle = self.send_cmd(cmd_string)
        resp = self.send_write_cmd(stream_handle, len(data), data)
        return resp
           
           
    def parse_fcr_args(self, cmd_args):                    
        # file_create [-[e][u]] [-o] <filename> <size> [<version> [<type> [<crc>]]]  
        file_info = {"essential":False, "unprotect":False, "stream":False, "name":"", "size":"0", "version":"1.0.0", "type": "0xFE", "crc":""}

          
        if "-o" in cmd_args != -1:
            file_info["stream"] = True
        if "-u" in cmd_args != -1:
            file_info["unprotect"] = True
        if "-e" in cmd_args != -1:
            file_info["essential"] = True
        if ("-eu" in cmd_args != -1) or ("-ue" in cmd_args):
            file_info["essential"] = True
            file_info["unprotect"] = True            
                    
        for i in range(len(cmd_args)):
            # Find first args that doenst have a "-" is it
            if cmd_args[i][0] != '-':
                #get all non flag args
                a = cmd_args[i:]
                
                file_info["name"] = a[0]
                file_info["size"] = a[1]
                try:
                    file_info["version"] = a[2]
                except IndexError:
                    pass
                try:
                    file_info["type"] = a[3]
                except IndexError:
                    pass
                try:
                    file_info["crc"] = a[4] 
                except IndexError:
                    pass               
                break
            
        return file_info
            
            
if __name__ == "__main__":
    import msvcrt
    a = wiconnectpy(sys.argv[1])
    
    if 0:
        f = "Redefining_the_Power_Benchmark.pdf"
        d = open(f, "rb").read()
        print a("fcr {} {}".format(f, len(d)), d)
        sys.exit(0)
        
    prompt = "> "
    
    print "Interactive Network Mode"
    sys.stdout.write(prompt)
    try:
        while(1):
            cmd_string = sys.stdin.readline().rstrip()
            if cmd_string.rstrip() == "exit":
                raise KeyboardInterrupt
            if cmd_string != "":
                cmd = cmd_string.split()[0] 
                cmd_args = cmd_string.split()[1:]              
                if ((cmd == "fcr" or cmd == "file_create") and (cmd_string.find("-o") == -1)) or (cmd == "write" or cmd == "stream_write"):
                    #capture cmd_string
                    if (cmd == "fcr" or cmd == "file_create"):
                        file_info = a.parse_fcr_args(cmd_args)
                        data_size = int(file_info["size"])
                    else:
                        data_size = int(cmd_args[1])
                    data = ""
                    # Capture data
                    # could add a timeout or escape option here
                    # not that the msvcrt.getwch only works for Windows.  Can use sys.stdin.read(1) for linux
                    while len(data) < int(data_size):
                        cmd_chr = msvcrt.getwch()
                        data += cmd_chr
                    resp = a(cmd_string, data)
                    sys.stdout.write(resp)
                else:
                    resp = a(cmd_string)
                    sys.stdout.write("{}".format(resp))
                sys.stdout.write("\n" + prompt)
            else:
                sys.stdout.write(prompt)
    except KeyboardInterrupt:
        sys.stdout.write("\nExiting")
        sys.exit(0)

            

        
        
        