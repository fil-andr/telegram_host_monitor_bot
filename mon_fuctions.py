import paramiko
import sqlalchemy as sa
import re
from paramiko.ssh_exception import AuthenticationException,NoValidConnectionsError
import socket
from threading import Thread

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


mem_var = ''
cpu_var = ''
io_var = ''
dsk_var = ''


def ssh_connect(connect_values):
    hostname, username, password = connect_values
    try:
        client.connect(hostname=hostname, username=username, password=password, look_for_keys=False, allow_agent=False,timeout=3)
    except AuthenticationException:
        return "Can not connect to host, invalid username or password"
    except NoValidConnectionsError:
        return f"Can not connect to host  {hostname}"
    except TimeoutError:
        return f"Can not connect to host  {hostname}, probably host is unreachable"
    except socket.timeout:
        return f"Can not connect to host  {hostname}, probably host is unreachable"
    thread_mem = Thread(target=memory_usage)
    thread_cpu = Thread(target=cpu_usage)
    thread_io = Thread(target=io)
    thread_dsk = Thread(target=dsk_usg)

    thread_mem.start()
    thread_cpu.start()
    thread_io.start()
    thread_dsk.start()

    thread_mem.join()
    thread_cpu.join()
    thread_io.join()
    thread_dsk.join()
    return result()


def result():
    return mem_var + cpu_var + io_var + dsk_var


def memory_usage():
    stdin, stdout, stderr = client.exec_command("free -m | grep Mem:")
    mem_lst = ''.join(stdout.readlines()).split()
    global mem_var
    mem_var = f'MEMORY STATS\nMemory usage: {int(mem_lst[2]) * 100 / int(mem_lst[1]):.2f}%\n __________________________________\n'
    return mem_var


def cpu_usage():
    stdin, stdout, stderr = client.exec_command("top -bn1 | grep %Cpu")
    cpu_lst = ''.join(stdout.readlines()).split()
    global cpu_var
    cpu_var = f'\nCPU\ncpu usage: {cpu_lst[1]}%\ncpu wait: {cpu_lst[9]}%\n __________________________________\n'
    return cpu_var


def io():
    stdin, stdout, stderr = client.exec_command("iostat -xd | awk '{ print $14 " " $1 }'")
    lst = stdout.readlines()
    lst.remove(lst[0])
    lst.remove(lst[0])
    lst.remove(lst[0])
    lst.remove(lst[len(lst) - 1])
    val_prc = []
    for i in lst:
        d = re.findall(r'\d+\.\d+', i)
        val_prc.append(d)
    dsk = []
    for i in lst:
        g = re.sub('\d+\.\d+', '', i).strip('\n')
        dsk.append(g)
    result = 'DISKS STATS\n'
    tmp_val = 0
    while tmp_val <= len(dsk) - 1:
        result += f'{dsk[tmp_val]} | utl%: {val_prc[tmp_val][0]}\n'
        tmp_val += 1
    global io_var
    io_var = result + '\n __________________________________\n'
    return io_var


def dsk_usg():
    stdin, stdout, stderr = client.exec_command(r"df -h | awk '{ print $5 "  " $6  }'")
    dsk_space_lst = ''.join(stdout.readlines()).split()
    dsk_space_lst.remove(dsk_space_lst[0])
    dsk_res = []
    res = ''
    for i in dsk_space_lst:
        dsk_res.append(i.split('%'))
    for i in dsk_res:
        res += f' {i[1]} --- use: {i[0]}%\n'
    global dsk_var
    dsk_var = res + '\n __________________________________\n'
    return dsk_var


##oracle db ts usage %
def ts_usage():
    engine = sa.create_engine('oracle://system:pswd_123@192.168.1.3:1521/test')
    ts_sel = engine.execute("select * from dba_data_files")
    res = ''
    for i in ts_sel:
        res += f'{i[2]}: usage %: {(i[11] * 100) / i[3]:.2f} \n'
    return res

