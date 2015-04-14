# The wiconnectpy module

The wiconnectpy module is for communicating with a WiConnect module via the WiConnect HTTP RESTful server.

It is written for python 2.7.

## Installing wiconnectpy

To install wiconnectpy, obtain a working copy from:

https://bitbucket.org/ackme/wiconnectpy

The wiconnectpy module requires the non-standard but commonly used python requests module. Install with pip or similar:
```pip install requests```

## Setting up the ACKme WiConnect Module

To set up your module to run the HTTP RESTful server, issue the following commands in a WiConnect terminal connected to your module:

```
set wlan.ssid               <YOUR SSID>
set wlan.passkey            <YOUR PASSWORD>
set wlan.auto_join.enabled  1    
set mdns.enabled            1
set mdns.name mymodule
set http.server.enabled     1
set http.server.api_enabled 1
save
reboot
```

The module response is similar to:
```
Rebooting
[Disassociated]
WiConnect-2.2.0.12, Built:2015-04-08 20:12:21 for AMW004.3, Board:AMW004-E03.3
[Ready]
[Associating to ackme]
> Security type from probe: WPA2-AES
Obtaining IPv4 address via DHCP
IPv4 address: 10.5.6.108
Starting mDNS
mDNS domain: mymodule.local
HTTP and REST API server listening on port: 80
[Associated]
```

The module now accepts HTTP requests from wiconnectpy.

## Running wiconnectpy

The wiconnectpy module runs in three possible modes:

* Interactive network mode
* Class mode with raw commands
* Class mode with structured commands

See (WiConnect online documentation)[http://wiconnect.ack.me] for full WiConnect documentation, including a complete description of all commands and variables.

### Interactive Network Mode

At a command line in the wiconnectpy working copy directory, run the command:
```
python wiconnectpy.py mymodule
```

This opens an interactive console similar to a WiConnect serial terminal connection. Issue commands and view the responses. For example:

```
.../wiconnectpy>python wiconnectpy.py mymodule
Interactive Network Mode
> get gp u
!  # Description
#  0 GPIO input_highz
#  1 system.indicator.wlan
#  2 system.indicator.network
#  5 system.indicator.softap
# 11 GPIO input_highz
# 13 UART1 RX
# 14 UART1 TX
# 17 SPI0 CLK
# 18 SPI0 MOSI
# 19 SPI0 MISO
# 21 GPIO output
# 22 GPIO output
```


### Class Mode with Raw Commands

The following demonstrates wiconnectpy running as a class with raw text commands. 

The python code below turns on User LED 1 on an ACKme Mackerel evaluation board:

```
import wiconnectpy

device = wiconnectpy.wiconnectpy(addr='mymodule.local')

device("set gpio.init 22 none") 
device("set gpio.init 22 out") 
device("gpio_set 22 1") 


```

Supply the URL of the ACKme module as the ``addr`` argument to the ``wiconnectpy.__init__`` function. 

This returns a device object, representing the ACKme WiConnect device. The device object can then be used for issuing commands. 

Any WiConnect command can be issued as the argument when calling the device. The call returns the WiConnect command response.

For example:

```
print device("ls -v") 
```

This results in printing a verbose list of files on the WiConnect device.

### Class Mode with Structured Commands

The python code below uses structured commands. 

Each wiconnect command is represented by a device method.

The first argument to the device method is a string containing the command parameters.

The second argument, when required, is the data sent immediately after issuing the command. This is required for commands such as `file_create` and `stream_write`. 

```
import wiconnectpy

file_data = '0123456789'
device = wiconnectpy.wiconnectpy('mymodule.local')
device.ls("-v")
device.fcr("blah.txt 10", file_data)
device.ls("-v")
```
 
### Listing Available Commands

`dir(device)` lists all the available commands. This list is generated dynamically by querying the module with the command `help commands` when first connecting.

### File Transfers
 
File transfers, in response to the `file_create` command, use CRC validation.

File transfer is implemented using HTTP posts to the WiConnect HTTP RESTful server.

All HTTP requests use base 64 encoding.

 
