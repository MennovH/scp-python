#! /usr/bin/env python3
import socket,subprocess,platform,sys,os,getopt
from colorama import Fore,Back,Style
from getpass import getpass

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0].rsplit(".", 1)[0]
subnet = get_ip()

package = 'sshpass'
try:
    command = f'which {package}'
    check = subprocess.getoutput(command)
    if not check:
        print (f'{Fore.RED}sshpass not installed\n{Fore.GREEN}installing...{Style.RESET_ALL}')
        subprocess.run(["sudo", "apt", "install", "-y", package], check=True)
except ValueError as e:
    print (f'{Fore.RED}{Back.WHITE}{package} could not be installed...{Style.RESET_ALL}')

def ipaddr(ip):
    try:
        if '.' in str(ip) or ':' in str(ip):
            socket.inet_aton(ip)
            print(f'{Fore.CYAN}IP address set to:{Style.RESET_ALL} {ip}')
            return
        elif 0 < int(ip) < 1000:
            ip = f'{subnet}.{ip}'
            print(f'{Fore.CYAN}IP address set:{Style.RESET_ALL} {ip}')
            return ip
    except ValueError as e:
        print(e)
        print(f'{Fore.RED}IP-address \"{ip}\" has been declined{Style.RESET_ALL}')
    ip = ''
    return ip

def usage(err):
    if err is not None and err != 0:
        print (err)
    print (f'{Style.RESET_ALL}Usage: {Fore.CYAN}{sys.argv[0]} [-h <help>] [-u <username>] [-i <ip-address>] [-w <timeout in seconds>] [<absolute path>]{Style.RESET_ALL}')
    
def send(user,ip,items,w):
    value = input_user = msg = item_type = ''
    try: int(w)
    except: w = 30
    if w == 1: print(f'{Fore.CYAN}Timeout (wait) set:{Style.RESET_ALL} {w} second')
    else:  print(f'{Fore.CYAN}Timeout (wait) set:{Style.RESET_ALL} {w} seconds')
    t = len(items)
    item_list = []
    for item in items:
        if os.path.isdir(item):
            item_list.append(f'folder: {item}')
        elif os.path.isfile(item):
            item_list.append(f'file: {item}')
    setting = [user,ip]
    i = 0
    while setting[0] == '' or setting[1] == '':
        try:
            if i > 1: i = 0
            if i == 0: value = 'Username'
            elif i == 1: value = f'IP (current subnet: {subnet}....)'
            if setting[i] == '':
                while setting[i] == '':
                    if i == 0: setting[i] = input(f'Enter the {value.lower()} of the receiver: ')
                    else: setting[i] = ipaddr(input(f'Enter the {value} of the receiver: '))
                    if setting[i] != '': print(f'{Fore.CYAN}{value} set:{Style.RESET_ALL} {setting[i]}')
            i += 1
            if t == 0:
                for a in range(6):
                    if t == 0: t = input_user = int(input('Enter the number of items: '))
                    else:
                        for b in range(t):
                            if input_user == 'exit': break
                            while 1:
                                input_user = input(f'Enter absolute path of item {b + 1}: ')
                                if input_user == 'exit': break
                                if input_user == 'show list': print('\n'.join())
                                if input_user == 'show list': print('\n'.join(f'{str(item_list.index(f)+1)}) {str(f)}' for f in item_list))
                                if input_user in item_list:
                                    print(f'{Fore.RED}Path "{input_user}" was already in list{Style.RESET_ALL}')
                                elif os.path.isdir(input_user):
                                    item_list.append(f'folder: {input_user}')
                                    print(f'{Fore.GREEN}Folder "{input_user}" was added to the list{Style.RESET_ALL}')
                                    break
                                elif os.path.isfile(input_user):
                                    item_list.append(f'file: {input_user}')
                                    print(f'{Fore.GREEN}File "{input_user}" was added to the list{Style.RESET_ALL}')
                                    break
                                elif input_user != 'show list':
                                    print(f'{Fore.RED}Path "{input_user}" doesn\'t exit{Style.RESET_ALL}')
        except (KeyboardInterrupt, Exception) as e:
            if (type(e).__name__) == 'KeyboardInterrupt' or t == 'exit': 
                msg = 'User ended the process'
                break
            continue
                
    s = f = k = 0
    key_check = 'cDHHu7t4JL161*dras*x@ewRGvXj*oLx@$H'
    if t > 0 and msg == '':
        password = getpass(f'Enter password for {setting[0]}: ')
        item_list.insert(0,key_check)
        stop_trying = True
        for attempt in range(3):
            if stop_trying == True and attempt > 0: break
            stop_trying = True
            for item in item_list:
                if item[:8] == 'folder: ': item_type = item[:8]
                elif item[:6] == 'file: ': item_type = item[:6]
                item = item.replace(item_type,'')
                if item_type == 'folder: ': item_type = f'{Fore.YELLOW}{item_type}{Style.RESET_ALL}'
                try:
                    if item == key_check: command = f'ssh-keygen -l -F {setting[1]}'
                    else: command = f'sshpass -p {password} scp -r {item} {setting[0]}@{setting[1]}:'
                    outs,errs = subprocess.Popen(args=command,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True).communicate(timeout=w)
                    if errs == '':
                        if item != key_check:
                            print(f'{Fore.GREEN}Sent to {setting[0]}\'s root folder:{Style.RESET_ALL} {item_type}{item}')                
                            s += 1
                    elif errs:
                        if 'Permission denied' in errs and attempt < 2:
                            password = getpass(f'Permission denied. Enter password for {setting[0]}: ')
                            errs = ''
                            stop_trying = False
                            break
                        if item != key_check:
                            print(f'{Fore.RED}Failed to send:{Style.RESET_ALL} {item_type}{item}\n{errs.strip()}')
                            f += 1
                    if item == key_check and outs.strip() == '':
                        print(f'\n{Fore.RED}Host {setting[1]} authentication could not be verified.\nTesting connection. When prompted for adding the host {setting[1]} to known_host, type \'yes\' and press \'Enter\' in order for this script to work. Only accept when the host is trusted.\nAfter accepting or declining the prompt, wait for the process to end. This process will be terminated in about 5 seconds after reading this message.{Style.RESET_ALL}\n')
                        command = f'ssh {setting[0]}@{setting[1]}'
                        output = subprocess.Popen(args=command,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
                        try: outs,errs = output.communicate(timeout=10)
                        except ValueError as e:
                            print(e)
                            pass
                        if outs == 'Host key verification failed.': f = t
                        if 'No route to host' in errs:
                            stop_trying = True
                            print ('Error message:',errs.replace('\n',''))
                            print(f'Failed to send:{Fore.RED}')
                            del item_list[0]
                            print(f'{Fore.RED}\n'.join(map(str, item_list)))
                            f = t
                            break
                        output.kill()
                        print('\nProcess terminated. Continuing scp...')
                        continue
                except (KeyboardInterrupt, Exception) as e:
                    if (type(e).__name__) == 'KeyboardInterrupt':
                        msg = 'User ended the process\n'
                        del item_list[0]
                        print(f'\nFailed to send:{Fore.RED}')
                        if os.path.isdir(item): item = f'folder: {item}'
                        else: item = f'file: {item}'
                        if item != key_check:
                            del item_list[0:item_list.index(item)]
                        print(f'{Fore.RED}\n'.join(map(str, item_list)))
                        break
                    else:
                        e = repr(e).replace(password,'**********')
                        if 'Timeout' in repr(e):
                            e = f'{Fore.RED}Timeout of {w} seconds exceeded...{Style.RESET_ALL}'
                        print(f'{Fore.RED}Failed to send:{Style.RESET_ALL} {item_type}{item}:',e)
                        f += 1
                        continue
    if s == t: msg += f'{Fore.GREEN}Sent: {s}/{t}{Style.RESET_ALL}'
    if s != t and s > 0: msg += f'{Fore.YELLOW}Sent: {s}/{t}{Style.RESET_ALL}'
    if f == t or s == 0: msg += f'{Fore.RED}Sent: {s}/{t}{Style.RESET_ALL}'
    print(msg)

if __name__ == '__main__':
    user = ip = ''
    w = 30
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'hu:i:w:', ['user','ip','w'])
        for opt, arg in opts:
            if opt in ('-h', '--help'): sys.exit(usage('Error occurred: {Fore.RED}{err}'))
            elif opt in ('-u', '--user'): user = arg 
            elif opt in ('-i', '--ip') and '.' in arg: ip = arg
            elif opt in ('-i', '--ip'): ip = int(arg)
            elif opt in ('-w', '--wait'): w = int(arg)
        if ip != '': ip = ipaddr(ip)            
        items = '$'.join(args)
        if '$' in items: items = items.split('$')
        else: items = [items]
    except (getopt.GetoptError,Exception) as err:
        sys.exit(usage(f'Error occurred: {Fore.RED}{err}'))
    send(user,ip,items,w)
