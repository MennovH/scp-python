#! /usr/bin/env python3
import socket,subprocess,platform,sys,os,getopt
from colorama import Fore,Back,Style
from getpass import getpass

red = Fore.RED
cyan = Fore.CYAN
green = Fore.GREEN
yellow = Fore.YELLOW
reset = Style.RESET_ALL

#get own subnet for easy input
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0].rsplit(".", 1)[0]
subnet = get_ip()

#check if sshpass is installed
package = 'sshpass'
try:
    command = f'which {package}'
    check = subprocess.getoutput(command)
    if not check:
        print (f'{red}sshpass not installed\n{green}installing...{reset}')
        subprocess.run(["sudo", "apt", "install", "-y", package], check=True)
except ValueError as e:
    print (f'{red}{Back.WHITE}{package} could not be installed...{reset}')

#check if ip is valid
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

#show help
def usage(err):
    if err is not None and err != 0:
        print (err)
    print (f'{reset}Usage: {cyan}{sys.argv[0]} [-h <help>] [-u <username>] [-i <ip-address>] [-w <timeout in seconds>] [<path(s)>]{reset}')

#send item(s)
def scp(user,ip,item_list,wait_period):
    value = input_user = msg = item_type = input_err = password = ''
    for x in [item for item in item_list if not os.path.isdir(item) and not os.path.isfile(item)]: del item_list[item_list.index(x)]
    b = c = i = input_user = retries = 0
    success = handled = []
    setting = [user.replace(' ',''),ip.replace(' ','')]
    try: int(wait_period)
    except: wait_period = 30
    if wait_period == 1: print(f'{cyan}Timeout (wait) set:{reset} {w} second')
    else: print(f'{cyan}Timeout (wait) set:{reset} {wait_period} seconds')
    while '' in setting:
        try:
            if i > 1: i = 0
            if i == 0: value = 'Username'
            elif i == 1: value = f'IP (current subnet: {subnet}....)'
            if setting[i] == '':
                if i == 0: setting[i] = input(f'Enter the {value.lower()} of the receiver: ')
                else: setting[i] = ipaddr(input(f'Enter the {value} of the receiver: '))
                if setting[i] != '': print(f'{cyan}{value} set:{reset} {setting[i]}')
            i += 1
        except (KeyboardInterrupt, Exception) as e:
            if (type(e).__name__) == 'KeyboardInterrupt' or input_user == 'exit':
                msg = 'User ended the process\n'
                break
    while len(item_list) == 0 and '' not in setting:
        try:
            if len(item_list) == 0 and c == 0: input_user = input(f'{input_err}Enter the number of items: {reset}')
            if input_user == 'exit':
                msg = 'User ended the process\n'
                break
            c = int(input_user) if int(input_user) > 0 else 0
            while len(item_list) < c:
                 input_user = input(f'Enter absolute path of item {b + 1}: ')
                 if input_user == 'exit': break
                 if input_user == 'show list':
                     print('\n'.join(f'{str(item_list.index(f)+1)}) {str(f)}' for f in item_list))
                     continue
                 if os.path.isdir(input_user): item_type = f'{yellow}folder{reset}'
                 elif os.path.isfile(input_user): item_type = 'file'
                 else:
                     print(f'{red}Path "{input_user}" doesn\'t exit{reset}')
                     continue
                 item = input_user
                 if item in item_list:
                     print(f'{red}Path "{input_user}" was already in list{reset}')
                 elif os.path.isdir(input_user) or os.path.isfile(input_user):
                     item_list.append(item)
                     if len(item_list) < c: i = '(type "show list" to see the status)'
                     else: i = ''
                     print(f'{green}{item_type}: {green}{item_list[-1]} was added to the list {i}{reset}')
                     b += 1
        except (KeyboardInterrupt, Exception) as e:
            if (type(e).__name__) == 'KeyboardInterrupt' or input_user == 'exit':
                msg = 'User ended the process\n'
                break
            input_err = f'{red}Invalid literal for int() with base 10: {input_user}\nEnter \'exit\' to stop or try again.\n{reset}'
            input_user = 0
            pass
    if len(item_list) > 0 and msg == '':
        for attempt in range(3):
            if retries == 0 and attempt > 0: break
            retries = 0
            for item in item_list:
                item_type = f'{yellow}folder{reset}' if os.path.isdir(item) else 'file'
                try:
                    if password == '': password = getpass(f'Enter password for {setting[0]}: ')
                    #check known_hosts
                    #if item == item_list[0]: command = f'ssh-keygen -l -F {setting[1]}'
                    command = f'sshpass -p {password} scp -o StrictHostKeyChecking=yes -r {item} {setting[0]}@{setting[1]}:'
                    out,err = subprocess.Popen(args=command,
                                                 shell=True,
                                                 stderr=subprocess.PIPE,
                                                 stdout=subprocess.PIPE,
                                                 universal_newlines=True).communicate(timeout=wait_period)
                    if err == '':
                        print(f'{green}Sent to {setting[0]}\'s root folder:{reset} {item_type}: {item}')
                        handled.append(item)
                    elif err:
                        if 'Permission denied' in err and attempt < 2:
                            retries = 1
                            password = getpass(f'Permission denied. Enter password for {setting[0]}: ')
                            err = ''
                            break
                        if 'Could not resolve hostname' in err or 'Host key verification failed.' in err or 'No route to host' in err:
                            msg = out if err == '' else err
                            if 'Could not resolve hostname' in err or 'Host key verification failed.' in err:
                                msg += f'{cyan}Try "ssh {setting[0]}@{setting[1]}" on the command line first, and type "yes" to accept {setting[1]} to be added to known_hosts{reset}\n'
                            break
                        else:
                            print(f'{red}Failed to send:{reset} {item_type}: {item}\n{err.strip()}')
                            handled.append(item)
                        continue
                except (KeyboardInterrupt, Exception,ValueError) as e:
                    if (type(e).__name__) == 'KeyboardInterrupt':
                        msg = 'User ended the process\n'
                        break
                    else:
                        e = repr(e).replace(password,'**********')
                        if 'Timeout' in repr(e):
                            e = f'{red}Timeout of {wait_period} seconds exceeded...{reset}'
                        elif 'Timeout' not in repr(e):
                            print(f'{red}Failed to send:{reset} {item_type}: {item}:',e)
                        continue
    #report
    if len(handled) != len(item_list):
        print('Failed to send:')
        for x in [item for item in item_list if item not in handled]:
            if os.path.isdir(x): item_type = f'{yellow}folder'
            else: item_type = 'file'
            print(f'{item_type}: {red}{x}')
    s = len(handled)
    t = len(item_list)
    f = t - s
    if s == t and s != 0: msg += f'{green}Sent: {s}/{t}{reset}'
    if s != t and s > 0: msg += f'{yellow}Sent: {s}/{t}{reset}'
    if f == t or s == 0: msg += f'{red}Sent: {s}/{t}{reset}'
    print(msg)

#start process
if __name__ == '__main__':
    user = ip = ''
    wait_period = 30
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'hu:i:w:', ['user','ip','w'])
        for opt, arg in opts:
            if opt in ('-h', '--help'): sys.exit(usage('Error occurred: {red}{err}'))
            elif opt in ('-u', '--user'): user = arg
            elif opt in ('-i', '--ip') and '.' in arg: ip = arg
            elif opt in ('-i', '--ip'): ip = int(arg)
            elif opt in ('-w', '--wait'): wait_period = int(arg)
        if ip != '': ip = ipaddr(ip)
        items = '$'.join(args)
        if '$' in items: items = items.split('$')
        else: items = [items]
    except (getopt.GetoptError,Exception) as err:
        sys.exit(usage(f'Error occurred: {red}{err}'))
    scp(user,ip,items,wait_period)