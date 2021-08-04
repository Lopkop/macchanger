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
       // _//\\\\ [Version]: 1.1
      ((` (( 
"""

colorama.init(autoreset=True)


def _validate_os(parser: argparse.ArgumentParser) -> None:
    """Validates operating system, OS must be either Linux or OS X"""
    if not (sys.platform.startswith('linux') or sys.platform.startswith('darwin')):
        parser.error(colorama.Fore.LIGHTYELLOW_EX + '[!] Operation system must be either linux or mac.')


def _validate_mac_address(parser: argparse.ArgumentParser, mac_address: str) -> None:
    """Validates MAC address that user specify"""
    if not mac_address:
        parser.error(colorama.Fore.LIGHTYELLOW_EX + '[!] Please specify a mac address, '
                                                    'use --help for more information.')
    if not re.match(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', mac_address) or len(mac_address) != 17:
        parser.error(colorama.Fore.LIGHTRED_EX + f'[-] Invalid MAC address.')


def _validate_interface(parser: argparse.ArgumentParser, interface: str) -> None:
    """Validates interface that user specify"""
    if not interface:
        parser.error(colorama.Fore.LIGHTYELLOW_EX + '[!] Please specify an interface, '
                                                    'use --help for more information.')
    try:
        subprocess.check_output(['ifconfig', interface])
    except subprocess.CalledProcessError:
        parser.error(colorama.Fore.LIGHTRED_EX + f'[-] interface "{interface}" does not exist.')


def _validate_all_requirements(parser: argparse.ArgumentParser, interface: str, mac_address: str) -> None:
    """Validates all requirements that must be checked"""
    _validate_os(parser)
    _validate_interface(parser, interface)
    _validate_mac_address(parser, mac_address)


def _set_arguments_and_get_parameters(parser: argparse.ArgumentParser):
    """Sets arguments and return user specify values"""
    parser.add_argument('-i', '--interface', dest='interface', help='Interface to change its MAC address')
    parser.add_argument('-m', '--mac', dest='new_mac', help='New MAC address')
    parameters = parser.parse_args()

    _validate_all_requirements(parser, parameters.interface, parameters.new_mac)
    return parameters


def get_current_mac(parser: argparse.ArgumentParser, parameters: argparse.Namespace):
    """Returns current mac address from interface that user specify"""
    _validate_all_requirements(parser, parameters.interface, parameters.new_mac)
    ifconfig_result = subprocess.check_output(['ifconfig', parameters.interface])
    mac_address = re.search(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', str(ifconfig_result))

    if mac_address:
        return mac_address.group(0)
    else:
        parser.error(colorama.Fore.LIGHTRED_EX + f'[-] Could not read MAC address.')


def change_mac(interface: str, new_mac: str):
    """Changes the mac address"""
    if sys.platform.startswith('darwin'):
        subprocess.call(f'sudo ifconfig {interface} ether {new_mac}', shell=True)
    if sys.platform.startswith('linux'):
        subprocess.call(f'ifconfig {interface} down', shell=True)
        subprocess.call(f'ifconfig {interface} hw ether {new_mac}', shell=True)
        subprocess.call(f'ifconfig {interface} up', shell=True)


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser()
    all_parameters = _set_arguments_and_get_parameters(main_parser)
    print(art)
    print(f'current MAC = {get_current_mac(main_parser, all_parameters)}')
    change_mac(all_parameters.interface, all_parameters.new_mac)

    if get_current_mac(main_parser, all_parameters) == all_parameters.new_mac:
        print(colorama.Fore.LIGHTGREEN_EX + f'[+] MAC address has been changed to {all_parameters.new_mac}')
    else:
        print(colorama.Fore.LIGHTRED_EX + f'[-] MAC address has not been changed to {all_parameters.new_mac}')
