'''
Created on 15 Jan 2015

@author: Chad

Modified for Gecko OS 29 May 2018: Neale
'''
import sys
import requests
import json
import base64
import binascii # for binascii.crc32() function


class default_cmd(object):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __call__(self, cmd_args="", data=""):
        print self.parent.send_cmd("{} {}".format(self.name, cmd_args), data)


class gecko_ospy(object):
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
        
        self.fcr_options = {
            "-c": {"name":"crc"          ,"boolean":False   ,"default":""},
            "-d": {"name":"devicekey"    ,"boolean":True    ,"default":False}, # device key           
            "-e": {"name":"essential"    ,"boolean":True    ,"default":False},
            "-l": {"name":"location"     ,"boolean":False   ,"default":""},
            "-p": {"name":"preencrypted" ,"boolean":False   ,"default":""},
            "-m": {"name":"permissions"  ,"boolean":False   ,"default":""},            
            "-t": {"name":"type"         ,"boolean":False   ,"default":"0x44"},
            "-u": {"name":"userencrypt"  ,"boolean":True    ,"default":False}, #user key: system.security_key
            "-v": {"name":"version"      ,"boolean":False   ,"default":""},
            }
        self.writeProgressMeter = False

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
            full_func = func.split(":")[0]
            short_func = func.split(":")[1]
            setattr(self.__class__, full_func, default_cmd(self, full_func))

            if short_func != full_func:
                setattr(self.__class__, short_func, default_cmd(self, short_func))

    def send_cmd(self, command, data=""):
        jsonData = json.dumps({"command": base64.b64encode(command), 
                    "flags": 0x7, # command, data and response are base64 encoded
                    "data": base64.b64encode(data)}) 
        
        try:
            a = requests.post(
                            self.url,  
                            data=jsonData,
                            headers={
                                "content-type": "application/json", 
                                "accepts": "application/json"
                            }, 
                            timeout=10
                            )
            if a.status_code == 200:
                return base64.b64decode(a.json()["response"]).rstrip() # response is correctly base64 encoded
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

        # Validate size
        try:
            if int(size) != len(data):
                print "Data size incorrect"
                return ""
        except:
            print "Data size wrong format"
            return ""

        # Send data in chunks to adhere to memory restrictions on module
        if self.writeProgressMeter: sys.stdout.write("Progress:   0%")
        init_size = float(len(data))
        while data:
            data_chunk = data[:self.MAX_CHUNK_SIZE]
            resp = self.send_cmd("write {} {}".format(stream_handle, len(data_chunk)), data_chunk)
            if resp != "Success":
                return ""
            data = data[self.MAX_CHUNK_SIZE:]
            if self.writeProgressMeter: 
                progress = (float(len(data)) / init_size) * 100
                sys.stdout.write("\rProgress: {:3d}%".format(100 - int(progress)))

        if self.writeProgressMeter: sys.stdout.write("\r                     \r")
        return resp

    def send_fcr_cmd(self, cmd_args, data):

        file_info = self.parse_fcr_args(cmd_args)
        if int(file_info["size"]) != len(data):
            print "Invalid file size"
            return ""

        crc = hex(binascii.crc32(str(data)))
        crc = crc.rstrip('L') # remove any L at the end
        
        if not file_info.get("crc",""):
            file_info["crc"] = '{}'.format(crc)
        elif str(crc) != file_info["crc"]:
            print "Invalid CRC"
            return ""
        # command has been changed so that options come after filesize
        
        option_str = " -o" # we always open the file this way
        
        for option, optD in self.fcr_options.items():
            if file_info.get(optD["name"],None):
                    option_str += " {o}".format(o=option)
                    if not optD["boolean"]:
                        option_str += " {v}".format(v=file_info[optD["name"]])

        cmd_string = "fcr {n} {s} {o}".format(n=file_info["name"], s=file_info["size"], o=option_str)

        stream_handle = self.send_cmd(cmd_string)
        resp = self.send_write_cmd(stream_handle, len(data), data)
        return resp

    def parse_fcr_args(self, cmd_args):
        # file_create [<filename> <size> options]
        file_info = {"name": cmd_args[0], "size": cmd_args[1]} # name and size are always the first two args in gecko_os
        
        lenCmdArgs = len(cmd_args)
        i = 2
        while i < lenCmdArgs:
            cmd_arg = cmd_args[i]
            optD = self.fcr_options.get(cmd_arg, None)
            if optD:
                if optD["boolean"]:
                    file_info[optD["name"]] = True
                else: # need the value
                    if i < lenCmdArgs-1:
                        i += 1
                        file_info[optD["name"]] = cmd_args[i]
            i += 1
        return file_info
    #------------------------ 
#----------------------------
def interactiveNetworkMode():

    import msvcrt
    
    a = gecko_ospy(sys.argv[1])
    a.writeProgressMeter = True
    
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
                if ((cmd == "fcr" or cmd == "file_create") and (cmd_string.find("-o") == -1)) \
                        or ((cmd == "write" or cmd == "stream_write")):
                    # capture cmd_string
                    if (cmd == "fcr") or (cmd == "file_create"):
                        file_info = a.parse_fcr_args(cmd_args)
                        data_size = int(file_info["size"])
                    else:
                        data_size = int(cmd_args[1])
                    data = ""
                    # Capture data
                    # could add a timeout or escape option here
                    # note that the msvcrt.getwch only works for Windows.  Can use sys.stdin.read(1) for linux
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
#----------------------------    
    
if __name__ == "__main__":
    interactiveNetworkMode()
    
    
    
    

