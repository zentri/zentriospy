import gecko_ospy

deviceIPv4 = '10.5.6.126'
device = gecko_ospy.gecko_ospy(addr=deviceIPv4)

def test_file_create():

    file_data = '0123456789'
    device.ls("-v")
    device.fcr("blah.txt 10", file_data)
    device.ls("-v")

def test_ls():
    device("ls -v")
    device.ls("-v")
    
print dir(device)
print
print test_ls()