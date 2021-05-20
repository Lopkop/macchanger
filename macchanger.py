"""
Simple mac address changer for Linux and MacOS.
Command line: python macchanger.py --help
"""

import subprocess
import argparse
import colorama
import sys
import re

art = r"""
\\             //
 \\\' ,      / //
  \\\//,   _/ //,
   \_-//' /  //<,
     \ ///  <//`
    /  >>  \\\`__/_
   /,)-^>> _\` \\\
   (/   \\ //\\ [Author]: Lopkop
       // _//\\\\ [Version]: 1.0
      ((` (( 
"""

colorama.init(autoreset=True)


def validate_mac_and_interface(parser: argparse.ArgumentParser, mac_address: str, interface: str):
    """Validates operating system, MAC address and interface that user specify"""
    if not (sys.platform.startswith('linux') or sys.platform.startswith('darwin')):
        parser.error(colorama.Fore.LIGHTYELLOW_EX + '[!] Operation system must be linux or mac.')
    if not interface:
        parser.error(
            colorama.Fore.LIGHTYELLOW_EX + '[!] Please specify an interface, use --help from more information.')
    if not mac_address:
        parser.error(
            colorama.Fore.LIGHTYELLOW_EX + '[!] Please specify a mac address, use --help from more information.')

    if not re.match(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', mac_address):
        parser.error(colorama.Fore.LIGHTRED_EX + f'[-] Invalid MAC address.')
    try:
        subprocess.check_output(['ifconfig', interface])
    except subprocess.CalledProcessError:
        parser.error(colorama.Fore.LIGHTRED_EX + f'[-] interface "{interface}" does not exist.')


def get_current_mac(parser: argparse.ArgumentParser, interface: str):
    """Returns current mac address from interface that user specify"""
    validate_mac_and_interface(parser, options.new_mac, options.interface)
    ifconfig_result = subprocess.check_output(['ifconfig', interface])
    mac_address = re.search(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', str(ifconfig_result))

    if mac_address:
        return mac_address.group(0)
    else:
        parser.error(colorama.Fore.LIGHTRED_EX + f'[-] Could not read MAC address.')


def set_arguments_and_get_options(parser: argparse.ArgumentParser):
    """Sets arguments and return user specify values"""
    parser.add_argument('-i', '--interface', dest='interface', help='Interface to change its MAC address')
    parser.add_argument('-m', '--mac', dest='new_mac', help='New MAC address')
    options = parser.parse_args()

    validate_mac_and_interface(parser, options.new_mac, options.interface)
    return options


def change_mac(interface: str, new_mac: str):
    """Changes the mac address"""
    if sys.platform.startswith('darwin'):
        subprocess.call(f'sudo ifconfig {interface} ether {new_mac}', shell=True)
    if sys.platform.startswith('linux'):
        subprocess.call(f'ifconfig {interface} down', shell=True)
        subprocess.call(f'ifconfig {interface} hw ether {new_mac}', shell=True)
        subprocess.call(f'ifconfig {interface} up', shell=True)


parser = argparse.ArgumentParser()
options = set_arguments_and_get_options(parser)
print(art)
if __name__ == '__main__':
    print(f'current MAC = {get_current_mac(parser, options.interface)}')
    change_mac(options.interface, options.new_mac)

    if get_current_mac(parser, options.interface) == options.new_mac:
        print(colorama.Fore.LIGHTGREEN_EX + f'[+] MAC address has been changed to {options.new_mac}')
    else:
        print(colorama.Fore.LIGHTRED_EX + f'[-] MAC address has not been changed to {options.new_mac}')
