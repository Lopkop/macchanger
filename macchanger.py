"""
Simple mac address changer for MacOS
Command line: python macchanger.py --help
"""

import re
import subprocess
import argparse
import colorama

art = r"""
\\             //
 \\\' ,      / //
  \\\//,   _/ //,
   \_-//' /  //<,
     \ ///  <//`
    /  >>  \\\`__/_
   /,)-^>> _\` \\\
   (/   \\ //\\ [Author]: Lopkop
       // _//\\\\ [Version]: 0.1
      ((` (( 
"""

colorama.init(autoreset=True)


def validate_mac_and_interface(parser, mac_address, interface):
    """Validates MAC address and interface"""
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


def get_current_mac(parser, interface):
    validate_mac_and_interface(parser, options.new_mac, options.interface)
    ifconfig_result = subprocess.check_output(['ifconfig', interface])
    mac_address = re.search(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', str(ifconfig_result))

    if mac_address:
        return mac_address.group(0)
    else:
        parser.error(colorama.Fore.LIGHTRED_EX + f'[-] Could not read MAC address.')


def get_options_and_arguments(parser):
    parser.add_argument('-i', '--interface', dest='interface', help='Interface to change its MAC address')
    parser.add_argument('-m', '--mac', dest='new_mac', help='New MAC address')
    options = parser.parse_args()

    validate_mac_and_interface(parser, options.new_mac, options.interface)
    return options


def change_mac(interface, new_mac):
    """This function changes the mac address"""
    subprocess.call(f'sudo ifconfig {interface} ether {new_mac}', shell=True)


parser = argparse.ArgumentParser()
options = get_options_and_arguments(parser)
print(art)
if __name__ == '__main__':
    print(f'current MAC = {get_current_mac(parser, options.interface)}')
    change_mac(options.interface, options.new_mac)

    if get_current_mac(parser, options.interface) == options.new_mac:
        print(colorama.Fore.LIGHTGREEN_EX + f'[+] MAC changed to {options.new_mac}')
    else:
        print(colorama.Fore.LIGHTRED_EX + f'[-] MAC did not changed to {options.new_mac}')
