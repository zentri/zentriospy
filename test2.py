from gecko_ospy import gecko_ospy
import sys
import binascii

def testNdm1():

    testFileName = "fred1"
    device = gecko_ospy(sys.argv[1])    

    response = device("ls -l")
    if testFileName in response:
        print "deleting test file {}".format(testFileName)
        device("fde {}".format(testFileName))
    
    data = "hi babe"
    crc = binascii.crc32(str(data))
    print 'data:{} crc:{}'.format(data, crc)
    
    cmd_string = 'fcr {} 7  -l extended -t 0x81'.format(testFileName)
    cmd = cmd_string.split()[0]
    cmd_args = cmd_string.split()[1:]
    file_info = device.parse_fcr_args(cmd_args)
    print 'file_info:{}'.format(file_info)
    device.send_fcr_cmd(cmd_args, data)
   
    
    print 
    
def testNdm2():
    device = gecko_ospy(sys.argv[1]) 
    command = "ls -v"
    print device(command)
   
    
#---------------------
testNdm1()
testNdm2()