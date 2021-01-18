#! /usr/bin/env python3
import socket, subprocess, platform, sys, os, getopt, re
from colorama import Fore, Back, Style
from getpass import getpass

if platform.system() == 'Linux':
    desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
else:
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

red = Fore.RED
cyan = Fore.CYAN
green = Fore.GREEN
yellow = Fore.YELLOW
reset = Style.RESET_ALL


# get own subnet for easy input
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
subnet = s.getsockname()[0].rsplit(".", 1)[0]


print(f'{yellow}NOTE: This program uses sshpass option -p to pass the password to scp. This is not considered safe.\nOnly use in your own environments.')


# check if sshpass is installed
package = 'sshpass'
try:
    command = f'which {package}'
    check = subprocess.getoutput(command)
    if not check:
        while 1:
            user_input = input(f'{red}sshpass is not installed.{reset} Install? y/n: {reset}') or 'n'
            if user_input == 'y' or user_input == 'n':
                break
        if user_input == 'y':
            print(f'{green}Installing,...{reset}')
            subprocess.run(["sudo", "apt", "install", "-y", package], check=True)
        else:
            sys.exit(f'{red}Not installed, program stopped...{reset}')
except ValueError as e:
    print(f'{red}{Back.WHITE}{package} could not be installed...{reset}')


# check if ip is valid
def ipaddr(ip):
    try:
        if '.' in str(ip) or ':' in str(ip):
            socket.inet_aton(ip)
            print(f'{cyan}IP address set to:{reset} {ip}')
        elif 0 < int(ip) < 1000:
            ip = f'{subnet}.{ip}'
            print(f'{cyan}IP address set:{reset} {ip}')
            return ip
    except ValueError as e:
        print(f'{red}IP-address \"{ip}\" has been declined{reset}')
    return ''


# show help
def usage(err):
    if err is not None and err != 0:
        print(err)
    print(f'{reset}Usage: {cyan}{sys.argv[0]} [-h <help>] [-a <action (s) or (d)>] [-u <username>] [-i <ip-address>] [-d <download>] [-w <timeout in seconds>] [<path(s)>]{reset}')


# send item(s)
def scp(user, ip, item_list, timeout, action):
    value = user_input = msg = item_type = input_err = password = ''
    for x in [item for item in item_list if action == 'Send' and (not os.path.isdir(item) and not os.path.isfile(item)) or item == '']:
        del item_list[item_list.index(x)]
    if action != '':
        print(f'{cyan}Action set: {reset}{action} {len(item_list)} item(s):')
        for item in item_list:
            if action == 's':
                if os.path.isdir(item):
                    print(f'{item} {yellow}(folder){reset}')
                else:
                    print(f'{item} (file)')
            else:
                print(f'{item} (item)')
    b = c = i = user_input = retries = 0
    success = handled = []
    setting = [action.replace(' ', ''), user.replace(' ', ''), ip.replace(' ', '')]
    try:
        int(timeout)
    except:
        timeout = 30
    print(f'{cyan}Timeout set:{reset} {timeout} second') if timeout == 1 else print(f'{cyan}Timeout set:{reset} {timeout} seconds')
    while '' in setting:
        try:
            if i > 2:
                i = 0
            if i == 0:
                value = 'Action'
            elif i == 1:
                value = 'Username'
            elif i == 2:
                value = f'IP (current subnet: {subnet}....)'
            if setting[i] == '':
                if i == 0:
                    user_input = input(f'send (s) or download (d)?: ').lower()
                    if user_input == 's' or user_input == 'd':
                        action = setting[i] = 'Send' if user_input == 's' else 'Download'
                if i == 1:
                    setting[i] = input(f'Enter the {value.lower()} of the receiver: ')
                elif i == 2:
                    setting[i] = ipaddr(input(f'Enter the {value} of the receiver: '))
                if setting[i] != '':
                    print(f'{cyan}{value} set:{reset} {setting[i]}')
            i += 1
        except (KeyboardInterrupt, Exception) as e:
            if type(e).__name__ == 'KeyboardInterrupt' or user_input == 'exit':
                msg = 'User ended the process\n'
                break
    if len(item_list) == 0:
        item_list_len = 0
    while len(item_list) == 0 and '' not in setting:
        try:
            if len(item_list) == 0 and c == 0:
                user_input = input(f'{input_err}Enter the number of items: {reset}')
            if user_input == 'exit':
                msg = 'User ended the process\n'
                break
            c = int(user_input) if int(user_input) > 0 else 0
            while len(item_list) < c:
                user_input = input(f'Enter absolute path of item {b + 1}: ')
                if user_input == 'exit':
                    break
                if user_input == 'show list':
                    print('\n'.join(f'{str(item_list.index(f) + 1)}) {str(f)}' for f in item_list))
                    continue
                if len(re.sub(r'[ ’‘\'"`]', '', user_input)) < len(user_input):
                    print(f'->{red} path may not be empty or contain ’‘\'"`{reset}')
                    continue
                if action == 'Send':
                    if os.path.isdir(user_input):
                        item_type = f'{yellow}folder{reset}'
                    elif os.path.isfile(user_input):
                        item_type = 'file'
                    else:
                        print(f'->{red} Path "{user_input}" doesn\'t exit{reset}')
                        continue
                else:
                    item_type = 'item'
                item = user_input
                if item in item_list:
                    print(f'->{red} Path "{user_input}" was already listed{reset}')
                elif os.path.isdir(user_input) or os.path.isfile(user_input) or action == 'Download':
                    item_list.append(item)
                    if len(item_list) < c:
                        i = '(type "show list" to see the status)'
                    else:
                        i = ''
                    print(f'->{green} added to list: {item_list[-1]} {reset}({item_type}) {i}{reset}')
                    b += 1
        except (KeyboardInterrupt, Exception) as e:
            if type(e).__name__ == 'KeyboardInterrupt' or user_input == 'exit':
                msg = 'User ended the process\n'
                break
            input_err = f'->{red} Invalid literal for int() with base 10: {user_input}\nEnter \'exit\' to stop or try again.\n{reset}'
            user_input = 0
            pass
    if item_list_len == 0 and len(item_list) > 0:
        print(f'{cyan}Action set: {reset}{action} {len(item_list)} item(s):')
        for item in item_list:
            if action == 'Send':
                if os.path.isdir(item):
                    print(f'{item} {yellow}(folder){reset}')
                else:
                    print(f'{item} (file)')
            else:
                print(f'{item} (item)')
    if len(item_list) > 0 and msg == '':
        for attempt in range(3):
            if retries == 0 and attempt > 0:
                break
            retries = 0
            for item in item_list:
                if action == 'Send':
                    item_type = f'{yellow}folder{reset}' if os.path.isdir(item) else 'file'
                try:
                    if password == '':
                        password = getpass(f'Enter password for {setting[1]}: ')
                    cmd = f'sshpass -p {password} scp -o StrictHostKeyChecking=yes -r {item} {setting[1]}@{setting[2]}:' if action == 'Send' else f'sshpass -p {password} scp -o StrictHostKeyChecking=yes -r {setting[1]}@{setting[2]}:/{item} {desktop}'
                    out, err = subprocess.Popen(args=cmd,
                                                shell=True,
                                                stderr=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                universal_newlines=True).communicate(timeout=timeout)
                    if err == '':
                        print(f'{yellow}(Possibly) downloaded to {desktop}{reset}: {item}') if action == 'Download' else print(f'{green}Sent to {setting[1]}\'s root folder:{reset} {item_type}: {item}')
                        handled.append(item)
                    else:
                        if 'Permission denied' in err and attempt < 2:
                            retries = 1
                            password = getpass(f'Permission denied. Enter password for {setting[1]}: ')
                            err = ''
                            break
                        if 'Could not resolve hostname' in err or 'Host key verification failed.' in err or 'No route to host' in err:
                            msg = out if err == '' else err
                            if 'Could not resolve hostname' in err or 'Host key verification failed.' in err:
                                msg += f'{cyan}Try "ssh {setting[1]}@{setting[2]}" on the command line first, and type "yes" to accept {setting[2]} to be added to known_hosts{reset}\n'
                            break
                        else:
                            if action == 'Download':
                                print(f'{red}Failed to download:{reset} {item_type}: {item}\n{err.strip()}')
                            else:
                                print(f'{red}Failed to send:{reset} {item_type}: {item}\n{err.strip()}')
                            handled.append(item)
                        continue
                except (KeyboardInterrupt, Exception, ValueError) as e:
                    if type(e).__name__ == 'KeyboardInterrupt':
                        msg = 'User ended the process\n'
                        break
                    else:
                        e = repr(e).replace(password, '**********')
                        if 'Timeout' in repr(e):
                            e = f'{red}Timeout of {timeout} seconds exceeded...{reset}'
                        elif 'Timeout' not in repr(e):
                            if action == 'Download':
                                print(f'{red}Failed to download:{reset} {item_type}: {item}:', e)
                            else:
                                print(f'{red}Failed to send:{reset} {item_type}: {item}:', e)
                        continue
    # report
    if len(handled) != len(item_list):
        print(f'Failed to {action.lower()}:')
        for x in [item for item in item_list if item not in handled]:
            if action == 'Download':
                item_type = 'item'
            elif os.path.isdir(x):
                item_type = f'{yellow}folder'
            else:
                item_type = 'file'
            print(f'{item_type}: {red}{x}{reset}')
    s = len(handled)
    t = len(item_list)
    if action == 'Download':
        msg += f'{yellow}(Possibly) downloaded: {s}/{t}{reset}'
    else:
        if s == t and s != 0:
            msg += f'{green}Sent: {s}/{t}{reset}'
        if s != t and s > 0:
            msg += f'{yellow}Sent: {s}/{t}{reset}'
        if (t - s) == t or s == 0:
            msg += f'{red}Sent: {s}/{t}{reset}'
    print(msg)


# start process
if __name__ == '__main__':
    user = ip = action = ''
    timeout = 30
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'ha:u:i:w:', ['action', 'user', 'ip', 'timeout'])
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                sys.exit(usage('Error occurred: {red}{err}'))
            elif opt in ('-a', '--action') and (arg == 's' or arg == 'd'):
                action = 'Send' if arg == 's' else 'Download'
            elif opt in ('-u', '--user'):
                user = arg
            elif opt in ('-i', '--ip') and '.' in arg:
                ip = arg
            elif opt in ('-i', '--ip'):
                ip = int(arg)
            elif opt in ('-t', '--timeout'):
                timeout = int(arg)
        if action != '':
            print(f'{cyan}Action set: {reset}{action}')
        if user != '':
            print(f'{cyan}Username set: {reset}{user}')
        if ip != '':
            ip = ipaddr(ip)
        items = '$'.join(args)
        if '$' in items:
            items = items.split('$')
        else:
            items = [items]
    except (getopt.GetoptError, Exception) as err:
        sys.exit(usage(f'Error occurred: {red}{err}'))
    scp(user, ip, items, timeout, action)
