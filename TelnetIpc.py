import telnetlib

def telnetTask( **kwargs):
    ip = kwargs['ip']
    cmds = kwargs['cmds']
    username = 'root'
    password = 'GmiINC200'
    finish = '# '
    timeout = 10
    try:
        tn = telnetlib.Telnet(ip, port=23, timeout=timeout)
    except Exception, msg:
        return [ip,["fail"]]    
    # tn.set_debuglevel(3)
    tn.read_until('login: ',timeout=timeout)
    tn.write(username + '\n')
    tn.read_until('Password: ',timeout=timeout)
    tn.write(password + '\n')
    tn.read_until(finish,timeout=timeout)
    ret = []
    for cmd in cmds:
        try:
            tn.write('%s\n' % cmd)
            ret.append(tn.read_until(finish,timeout=timeout))
            
        except Exception, msg:
            ret = ['fail']
            break
    tn.close()
    return [ip,ret]

# print telnetTask("10.0.11.4","/opt/bin/dramsize")