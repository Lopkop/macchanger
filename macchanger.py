"""
Simple mac address changer for Linux and MacOS.
Command line: python macchanger.py --help
"""

import subprocess
import argparse
import random

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
       // _//\\\\ [Version]: 1.3
      ((` (( 
"""

colorama.init(autoreset=True)


def _validate_os(parser: argparse.ArgumentParser) -> None:
    """Validates operating system, OS must be either Linux or OS X"""
    if not (sys.platform.startswith('linux') or sys.platform.startswith('darwin')):
        parser.error(colorama.Fore.LIGHTYELLOW_EX + '[!] Operating system must be either linux or OS X.')


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


def _set_arguments_and_get_parameters(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """Sets arguments and return user specify values"""
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('-i', '--interface', dest='interface', help='Interface to change its MAC address')
    group.add_argument('-m', '--mac', dest='new_mac', help='New MAC address')
    group.add_argument('-r', '--random', dest='random_mac', help='Generates random MAC address', required=False,
                       action='store_true')
    group.add_argument('-gcm', '--get-current-mac', dest='current_mac', help='Get current MAC address',
                       action='store_true', required=False)
    parameters = parser.parse_args()

    if not (parameters.current_mac or parameters.random_mac):
        _validate_all_requirements(parser, parameters.interface, parameters.new_mac)
    return parameters


def get_random_mac() -> str:
    """Generates random MAC address"""
    return ':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)])


def get_current_mac(parser: argparse.ArgumentParser, parameters: argparse.Namespace) -> str:
    """Returns current MAC address from interface that user specify"""
    _validate_interface(parser, parameters.interface)
    ifconfig_result = subprocess.check_output(['ifconfig', parameters.interface])
    mac_address = re.search(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', str(ifconfig_result))

    if mac_address:
        return mac_address.group(0)
    else:
        parser.error(colorama.Fore.LIGHTRED_EX + f'[-] Could not read MAC address.')


def change_mac(interface: str, mac_address: str) -> None:
    """Changes the mac address"""
    if sys.platform.startswith('darwin'):
        subprocess.call(f'sudo ifconfig {interface} ether {mac_address}', shell=True)
    if sys.platform.startswith('linux'):
        subprocess.call(f'ifconfig {interface} down', shell=True)
        subprocess.call(f'ifconfig {interface} hw ether {mac_address}', shell=True)
        subprocess.call(f'ifconfig {interface} up', shell=True)


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser(description='Simple mac address changer for Linux and OS X.')
    arguments = _set_arguments_and_get_parameters(main_parser)
    print(art)
    if arguments.current_mac:
        print(f'current MAC = {get_current_mac(main_parser, arguments)}')
        exit()
    print(f'current MAC = {get_current_mac(main_parser, arguments)}')

    random_mac = get_random_mac()
    if arguments.random_mac:
        change_mac(arguments.interface, random_mac)
    else:
        change_mac(arguments.interface, arguments.new_mac)

    if get_current_mac(main_parser, arguments) == (new_mac := arguments.new_mac or random_mac):
        print(colorama.Fore.LIGHTGREEN_EX + f'[+] MAC address has been changed to {new_mac}')
    else:
        print(colorama.Fore.LIGHTRED_EX + f'[-] MAC address has not been changed to {new_mac}')
