# The zentriospy module

The zentriospy module is for communicating with a ZentriOS module via the ZentriOS HTTP RESTful server.

It is written for python 2.7.

## Installing zentriospy

To install zentriospy, obtain a working copy from:

https://github.com/zentri/zentriospy

The zentriospy module requires the non-standard but commonly used python requests module. Install with pip or similar:
```pip install requests```

## Setting up the ZentriOS Module

To set up your module to run the HTTP RESTful server, issue the following commands in a serial terminal connected to your module:

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
ZentriOS-2.2.0.12, Built:2015-04-08 20:12:21 for AMW004.3, Board:AMW004-E03.3
[Ready]
[Associating to zentri]
> Security type from probe: WPA2-AES
Obtaining IPv4 address via DHCP
IPv4 address: 10.5.6.108
Starting mDNS
mDNS domain: mymodule.local
HTTP and REST API server listening on port: 80
[Associated]
```

The module now accepts HTTP requests from zentriospy.

## Running zentriospy

The zentriospy module runs in three possible modes:

* Interactive network mode
* Class mode with raw commands
* Class mode with structured commands

See (ZentriOS online documentation)[http://docs.zentri.com] for full ZentriOS documentation, including a complete description of all commands and variables.

### Interactive Network Mode

At a command line in the zentriospy working copy directory, run the command:
```
python zentriospy.py mymodule
```

This opens an interactive console similar to a ZentriOS serial terminal connection. Issue commands and view the responses. For example:

```
.../zentriospy>python zentriospy.py mymodule
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

The following demonstrates zentriospy running as a class with raw text commands. 

The python code below turns on User LED 1 on an Zentri Mackerel evaluation board:

```
import zentriospy

device = zentriospy.zentriospy(addr='mymodule.local')

device("set gpio.init 22 none") 
device("set gpio.init 22 out") 
device("gpio_set 22 1") 


```

Supply the URL of the Zentri module as the ``addr`` argument to the ``zentriospy.__init__`` function. 

This returns a device object, representing the ZentriOS device. The device object can then be used for issuing commands. 

Any ZentriOS command can be issued as the argument when calling the device. The call returns the ZentriOS command response.

For example:

```
print device("ls -v") 
```

This results in printing a verbose list of files on the ZentriOS device.

### Class Mode with Structured Commands

The python code below uses structured commands. 

Each ZentriOS command is represented by a device method.

The first argument to the device method is a string containing the command parameters.

The second argument, when required, is the data sent immediately after issuing the command. This is required for commands such as `file_create` and `stream_write`. 

```
import zentriospy

file_data = '0123456789'
device = zentriospy.zentriospy('mymodule.local')
device.ls("-v")
device.fcr("blah.txt 10", file_data)
device.ls("-v")
```
 
### Listing Available Commands

`dir(device)` lists all the available commands. This list is generated dynamically by querying the module with the command `help commands` when first connecting.

### File Transfers
 
File transfers, in response to the `file_create` command, use CRC validation.

File transfer is implemented using HTTP posts to the ZentriOS HTTP RESTful server.

All HTTP requests use base 64 encoding.

 
