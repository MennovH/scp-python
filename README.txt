scp-python.py

This python script can only be used on Linux (tested on Kali and Ubuntu).

This script can be used to easily send or download files and/or folders at once,
without having to enter a password per item.

This script doesn't add hosts to the known_hosts file. The hosts must be known already in order
for it to work. This is also a safety measure.

If not already made executable:
    sudo chmod u+x scp-python.py
or
    python3 scp-python.py

When it's executable by itself:
    ./scp-python.py

The process needs sshpass to connect the password to the scp process. If not already installed,
this script will start the installation automatically. Root access may be required.

It's possible to add comments on the command line. Sometimes even recommended:
    -u: receiving hostname
    -i: ip address of receiving host
    -w: change timeout period in seconds (standard=30) for larger files and/or folders
    -g: get/download. This option does not require an argument

Recommendation:
    Add the paths of the files and/or folders when executing the script. Otherwise, you need to
	add the paths by typing the paths in full later on. Some paths can be added to the send-list
	by entering the relative path. This, of course, will be checked whilst adding items to the list.

This script does not delete and/or alter any files, folders, permissions, etc. It also doesn't need any
connections to or from other IP addresses then what is provided by you, the user.

The only IP checks made are:
- the home subnet, which is a handy feature when sending to hosts within the same x.x.x.y subnet.
  In these cases, only the y will be needed. Feel free to type in the whole IP address everytime, though.
- all the IP addresses provided by the user, only to validate the IP addresses.
