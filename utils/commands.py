import logging, sys, os, time
import paramiko

sys.path.append(os.path.dirname(os.getcwd()))
# from automation.config import HOSTNAME

logging.basicConfig(level=logging.INFO)

def mk_dir(username, hostname):

    # setup a SSHClient object
    ssh = paramiko.SSHClient()

    # 允许将信任的主机自动加入到host_allow 列表，此方法必须放在connect方法的前面
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # connect to host
    try:
        ssh.connect(hostname=hostname, port=22, username='seluser', password='seluser')
    except Exception as e:
        raise
    
    # execute the command
    dir_name = '/home/seluser/Downloads/'+ username

    try:
        stdin, stdout, stderr = ssh.exec_command('mkdir '+ dir_name)
    except Exception as e:
        logging.error(e)
    
    # logging the output
    logging.debug('stdout: %s, \nstderr: %s'%(stdout, stderr))
    # logging.debug('sleeping! ')
    # time.sleep(300)
    # close the connection
    ssh.close()

    return dir_name

def send_to_ftpserver(hostname, fn):
        # setup a SSHClient object
    ssh = paramiko.SSHClient()

    # 允许将信任的主机自动加入到host_allow 列表，此方法必须放在connect方法的前面
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # connect to host
    try:
        ssh.connect(hostname=hostname, port=22, username='tst', password='tsttsttst')
    except Exception as e:
        raise
    else:
        sftp = paramiko.SFTPClient.from_transport(ssh)
        sftp.put(fn)

    ssh.close()

def set_environment(hostname='', value=1):
    # setup a SSHClient object
    ssh = paramiko.SSHClient()

    # 允许将信任的主机自动加入到host_allow 列表，此方法必须放在connect方法的前面
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # connect to host
    try:
        ssh.connect(hostname=hostname, port=22, username='tst', password='tsttsttst')
    except TimeoutError as e:
        raise
    else:
        stdin, stdout, stderr = ssh.exec_command('ls')
        for line in stdout:
            print('stdout',line)

        for line in stderr:
            print('stderr',line)
        logging.debug('end send to ftp')
    ssh.close()

if __name__ == '__main__':
    # trigger_send_to_ftpserver(HOSTNAME)
    # set_environment(hostname='9.112.56.150')
    send_to_ftpserver('9.112.56.150', )