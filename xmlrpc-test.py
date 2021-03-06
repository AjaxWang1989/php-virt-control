#!/bin/python3

import sys
import xmlrpc.client

# Change to valid data
apikey = "<apikey>"
address = "http://localhost/php-virt-control/xmlrpc.php"
selections = ['Information', 'Domain', 'Get network information']
info_types = ['connection', 'node', 'cpustats', 'eachcpustats', 'memstats', 'system']
domactions = ['Start', 'Stop', 'Reboot', 'Dump', 'Migrate', 'Get screenshot']
request = {'apikey': apikey,
           'connection': {'uri': 'qemu:///system'}
         }

# Should bail on this
connection_uri2 = 'qemu:///system';

request_info = request
request_info['data'] = {'type': 'unknown'}

request_name = request
request_name['data'] = {'name': 'x'}

def choose(prompt, chooser, types):
    print("\n%s types:\n" % chooser)
    num = 0
    for onetype in types:
        print("\t%s) %s" % (num + 1, types[num]))
        num += 1
    print("\n")
    line = input(prompt)
    try:
        return int(line) - 1
    except:
        return -1

try:
    print("XML RPC Proxy is set to %s" % address)
    if input("Is that OK? (Y/n) ") == "n":
        address = input("Enter new address: ")

    proxy = xmlrpc.client.ServerProxy(address)

    request['connection']['uri'] = 'list'
    conns = proxy.Information.get(request)
    conns_s = sorted(conns)

    print("\n")
    for connection in conns_s:
        print("%s) %s" % (int(connection) + 1, conns[connection]['name']))
    print("\n")

    line = input("Choose connection: ")
    try:
        conn = int(line) - 1
    except:
        sys.exit(1)

    conn = str(conn)
    request['connection']['uri'] = conns[conn]['uri']
    request_info['connection']['uri'] = request['connection']['uri']
    request_name['connection']['uri'] = request['connection']['uri']

    print("\nConnection URI: %s" % request['connection']['uri'])

    num = choose("Enter type: ", "Type", selections)
    if num == 0:
        num = choose("Enter your choice: ", "Information", info_types)
        if num > -1:
            request['data']['type'] = info_types[num]

            print("Result is: %s" % proxy.Information.get(request_info))
    elif num == 1:
        l = proxy.Domain.list(request)
        print("Domains:\n")
        for d in l:
            print("%s) %s" % (int(d) + 1, l[d]))
        print("\n")
        line = input("Choose domain index: ")
        try:
            idx = int(line) - 1
        except:
            sys.exit(1)

        # Assign the name to request_name dictionary
        name = l[str(idx)]
        request_name['data']['name'] = name

        l = proxy.Domain.info(request_name)
        print("\nDomain information:\n\nName: %s\nvCPUs: %s\nState: %s\nMemory: %s MiB (max %s MiB)\nCPUUsed: %s" %
            (name, l['nrVirtCpu'], l['state'], l['memory'] / 1024, l['maxMem'] / 1024, l['cpuUsed']))
        print("\nFeatures: %s\nMultimedia:\n\tInput: %s\n\tVideo: %s\n\tConsole: %s\n\tGraphics: %s\nHost devices: %s\nBoot devices: %s\n" %
            (l['features'], l['multimedia']['input'], l['multimedia']['video'], l['multimedia']['console'],
             l['multimedia']['graphics'], l['devices'], l['boot_devices']))
        num = choose("Enter your choice: ", "Domain actions", domactions)
        if num == -1:
            sys.exit(1)

        # Process actions
        if num == 0:
            print("Starting up domain %s" % name)
            print("Method returned: %s" % proxy.Domain.start(request_name)['msg'])
        elif num == 1:
            print("Stopping domain %s" % name)
            print("Method returned: %s" % proxy.Domain.stop(request_name)['msg'])
        elif num == 2:
            print("Rebooting %s" % name)
            print("Method returned: %s" % proxy.Domain.reboot(request_name)['msg'])
        elif num == 3:
            print("Dumping %s" % name)
            print("Method returned:\n%s" % proxy.Domain.dump(request_name)['msg'])
        elif num == 4:
            print("Migrating %s" % name)
            request_domain_migrate = request_name
            request_domain_migrate['data']['destination'] = {'uri': connection_uri2}

            print("Method returned: %s" % proxy.Domain.migrate(request_domain_migrate)['msg'])
        elif num == 5:
            print("Getting screenshot of %s" % name)
            print("Method returned: %s" % proxy.Domain.get_screenshot(request_name)['msg'])
    elif num == 2:
        l = proxy.Network.list(request)
        print("Network:\n")
        for d in l:
            print("%s) %s" % (int(d) + 1, l[d]))
        print("\n")
        line = input("Choose network index: ")
        try:
            idx = int(line) - 1
        except:
            sys.exit(1)

        # Assign the name to request_name dictionary
        name = l[str(idx)]
        request_name['data']['name'] = name

        print("Getting information about %s" % name)
        print("Method returned: %s" % proxy.Network.info(request_name))

except xmlrpc.client.ProtocolError as err:
    print("A protocol error occurred")
    print("URL: %s" % err.url)
    print("HTTP/HTTPS headers: %s" % err.headers)
    print("Error code: %d" % err.errcode)
    print("Error message: %s" % err.errmsg)
