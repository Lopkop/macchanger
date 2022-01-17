"""
Simple mac address changer for Linux and MacOS.
Command line: python macchanger.py --help
"""

import argparse
import random
import re
import sys
import subprocess

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
       // _//\\\\ [Version]: 1.4
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


def _set_arguments_and_get_parameters(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """Sets arguments and return user specify values"""
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('-i', '--interface', dest='interface', help='Interface to change its MAC address')
    group.add_argument('-m', '--mac', dest='custom_mac', help='Set a custom MAC address')
    group.add_argument('-r', '--random', dest='random_mac', help='Generate random MAC address',
                       action='store_true', required=False)
    group.add_argument('-gcm', '--get-current-mac', dest='current_mac', help='Get current MAC address',
                       action='store_true', required=False)
    group.add_argument('-p', '--permanent', dest='permanent_mac', help='Reset the MAC address to the permanent',
                       action='store_true', required=False)
    parameters = parser.parse_args()

    return parameters


def get_permanent_mac(interface: str) -> str:
    if sys.platform.startswith('darwin'):
        mac = subprocess.run(f'networksetup -getmacaddress {interface}', shell=True, capture_output=True)
    elif sys.platform.startswith('linux'):
        mac = subprocess.run(f'ethtool -P {interface}', shell=True, capture_output=True)
    return re.search(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', str(mac)).group(0)


def get_current_mac(interface: str) -> str:
    """Returns current MAC address from interface that user specify"""
    ifconfig_result = subprocess.check_output(['ifconfig', interface])
    mac_address = re.search(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', str(ifconfig_result))

    if mac_address:
        return mac_address.group(0)
    else:
        print(colorama.Fore.LIGHTRED_EX + f'[-] Could not read MAC address.')
        exit()


def get_random_mac() -> str:
    """Generates random MAC address"""
    return ':'.join(f'{random.randint(0, 255):02x}' for _ in range(6))


def change_mac(interface: str, mac_address: str) -> None:
    """Changes the mac address"""
    if sys.platform.startswith('darwin'):
        subprocess.call(f'sudo ifconfig {interface} ether {mac_address}', shell=True)
    elif sys.platform.startswith('linux'):
        subprocess.call(f'ifconfig {interface} down', shell=True)
        subprocess.call(f'ifconfig {interface} hw ether {mac_address}', shell=True)
        subprocess.call(f'ifconfig {interface} up', shell=True)


def verify_mac_change_and_print_result(interface: str, mac: str) -> str:
    return (colorama.Fore.LIGHTGREEN_EX + f'[+] MAC address has been changed to {mac}' if
            get_current_mac(interface) == mac else
            colorama.Fore.LIGHTRED_EX + f'[-] MAC address has not been changed to {mac}')


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser(description='Simple mac address changer for Linux and OS X.')
    arguments = _set_arguments_and_get_parameters(main_parser)

    _validate_os(main_parser)
    _validate_interface(main_parser, arguments.interface)
    if not (arguments.current_mac or arguments.random_mac or arguments.permanent_mac):
        _validate_mac_address(main_parser, arguments.custom_mac)

    print(art)
    if arguments.current_mac:
        print(colorama.Style.BRIGHT + f'current MAC = {get_current_mac(arguments.interface)}')
        exit()
    print(colorama.Style.BRIGHT + f'current MAC = {get_current_mac(arguments.interface)}')

    permanent_mac = get_permanent_mac(arguments.interface)
    if arguments.random_mac:
        random_mac = get_random_mac()
        change_mac(arguments.interface, random_mac)
        print(verify_mac_change_and_print_result(arguments.interface, random_mac))
    elif custom_mac := arguments.custom_mac:
        change_mac(arguments.interface, custom_mac)
        print(verify_mac_change_and_print_result(arguments.interface, custom_mac))
    else:
        change_mac(arguments.interface, permanent_mac)
        print(verify_mac_change_and_print_result(arguments.interface, permanent_mac))
