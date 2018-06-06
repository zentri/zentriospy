# The gecko_ospy module

The gecko_ospy module is for communicating with a Gecko OS module via the Gecko OS HTTP RESTful server.

It is written for python 2.7.

## Installing gecko_ospy

To install gecko_ospy, obtain a working copy from:

https://github.com/zentri/gecko_ospy

The gecko_ospy module requires the non-standard but commonly used python requests module. Install with pip or similar:
```
pip install requests
```

It also requires the `crcmod` module:
```
pip install crcmod
```

## Setting up the Gecko OS Module

To set up your module to run the HTTP RESTful server, issue the following commands in a serial terminal connected to your module:

```
set wlan.ssid               <YOUR SSID>
set wlan.passkey            <YOUR PASSWORD>
set wlan.auto_join.enabled  1    
set http.server.enabled     1
set http.server.api_enabled 1
save
reboot
```

The module response is similar to:
```
Rebooting
[Disassociated]
Gecko_OS-2.2.0.12, Built:2015-04-08 20:12:21 for AMW004.3, Board:AMW004-E03.3
[Ready]
[Associating to <YOUR SSID>]
> Security type from probe: WPA2-AES
Obtaining IPv4 address via DHCP
IPv4 address: 10.5.6.108
HTTP and REST API server listening on port: 80
[Associated]
```

The module now accepts HTTP requests from gecko_ospy.

## Running gecko_ospy

The gecko_ospy module runs in three possible modes:

* Interactive network mode
* Class mode with raw commands
* Class mode with structured commands

See (Gecko OS online documentation)[http://docs.zentri.com] for full  documentation, including a complete description of all commands and variables.

### Interactive Network Mode

At a command line in the gecko_ospy working copy directory, run the command:
```
python gecko_ospy.py mymodule
```

Alternatively use the Gecko OS device IP address, e.g.
```
python gecko_ospy.py 10.5.6.123
```


This opens an interactive console similar to a Gecko OS serial terminal connection. Issue commands and view the responses. For example:

```
.../gecko_ospy>python gecko_ospy.py mymodule
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

The following demonstrates gecko_ospy running as a class with raw text commands. 

The python code below turns on User LED 1 on an Zentri Mackerel evaluation board:

```
import gecko_ospy

device = gecko_ospy.gecko_ospy(addr='10.5.6.123')

device("set gpio.init 22 none") 
device("set gpio.init 22 out") 
device("gpio_set 22 1") 


```

Supply the URL of the Zentri module as the ``addr`` argument to the ``gecko_ospy.__init__`` function. 

This returns a device object, representing the Gecko OS device. The device object can then be used for issuing commands. 

Any Gecko OS command can be issued as the argument when calling the device. The call returns the Gecko OS command response.

For example:

```
print device("ls -v") 
```

This results in printing a verbose list of files on the Gecko OS device.

### Class Mode with Structured Commands

The python code below uses structured commands. 

Each Gecko OS command is represented by a device method.

The first argument to the device method is a string containing the command parameters.

The second argument, when required, is the data sent immediately after issuing the command. This is required for commands such as `file_create` and `stream_write`. 

```
import gecko_ospy

file_data = '0123456789'
device = gecko_ospy.gecko_ospy('mymodule.local')
device.ls("-v")
device.fcr("blah.txt 10", file_data)
device.ls("-v")
```
 
### Listing Available Commands

`dir(device)` lists all the available commands. This list is generated dynamically by querying the module with the command `help commands` when first connecting.

### File Transfers
 
File transfers, in response to the `file_create` command, use CRC validation.

File transfer is implemented using HTTP posts to the Gecko OS HTTP RESTful server.

All HTTP requests use base 64 encoding.

 
