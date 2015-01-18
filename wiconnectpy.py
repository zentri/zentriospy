'''
Created on 15 Jan 2015

@author: Chad
'''
import sys
import requests
import json
import base64


class wiconnectpy(object):
    '''
    classdocs
    '''
    MAX_CHUNK_SIZE = 2500
    
    def __init__(self, addr, timeout=12, retries=1):
        '''
        Constructor
        '''
        self.addr = addr
        self.timeout = timeout
        self.retries = retries
        self.data_buffer = ""

    
    def __call__(self, cmd_string, data=""):
        self.url = "http://" + self.addr + "/command"
        
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
        
        
    def send_cmd(self, command, data=""):
        try:
            a = requests.post(self.url,  data=json.dumps({"command": base64.b64encode(command), "flags":0x7, "data": base64.b64encode(data)}), headers={"content-type":"application/json", "accepts":"application/json"})  
            if a.status_code == 200:
                return base64.b64decode(a.json()["response"]).rstrip()

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
        #Find and validate the file size  
        cmd_string = "fcr -o "
        for i in range(len(cmd_args)):
            cmd_string += cmd_args[i] + ' '
        
        if self.get_fcr_size(cmd_args) != len(data):
            print "Invalid file size"
            return ""

        stream_handle = self.send_cmd(cmd_string)
        resp = self.send_write_cmd(stream_handle, len(data), data)
        return resp
                    
    def get_fcr_size(self, cmd_args):    
        for i in range(len(cmd_args)):
            if cmd_args[i][0] != '-':
                if (i+1) < len(cmd_args):
                    try:
                        int(cmd_args[i+1])
                        return int(cmd_args[i+1])
                    except TypeError:
                        print "Invalid file size"
                        return False
        return False
            
            
if __name__ == "__main__":
    import msvcrt
    a = wiconnectpy(sys.argv[1])
    
    f = "STM32_ADC_Modes.pdf"
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
                        data_size = a.get_fcr_size(cmd_args)
                    else:
                        data_size = int(cmd_args[1])
                    data = ""
                    while len(data) < int(data_size):
                        cmd_chr = msvcrt.getwch()
                        data += cmd_chr
                    resp = a(cmd_string, data)
                    sys.stdout.write(resp)
                else:
                    sys.stdout.write(a(cmd_string))
                sys.stdout.write("\n" + prompt)
            else:
                sys.stdout.write(prompt)
    except KeyboardInterrupt:
        sys.stdout.write("\nExiting")
        sys.exit(0)

            

        
        
        