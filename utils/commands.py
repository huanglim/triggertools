import logging, sys, os, time
from configs import config
import paramiko

sys.path.append(os.path.dirname(os.getcwd()))
# from automation.config import HOSTNAME

def send_to_sftpserver(request, dir=None):
        # setup a SSHClient object
    if not dir:
        dir = os.path.join(config.DEFAULT_DIR, request.request['user'])

    ssh = paramiko.SSHClient()

    # 允许将信任的主机自动加入到host_allow 列表，此方法必须放在connect方法的前面
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # connect to host
    try:
        ssh.connect(hostname=config.SFTP_HOSTIP,
                    port=config.SFTP_PORT,
                    username=config.SFTP_USERNAME,
                    password=config.SFTP_PASSWORD,
                    timeout=15)
    except Exception as e:
        raise
    else:
        stdin, stdout, stderr = ssh.exec_command('ls')
        for line in stdout:
            print('stdout',line)

        for line in stderr:
            print('stderr',line)
        sftp = paramiko.SFTPClient.from_transport(ssh)

    for file in os.listdir(dir):
        try:
            sftp.put(file)
        except Exception as e:
            raise
        else:
            os.remove(os.path.join(dir, file))

    ssh.close()

def mkdir(user):
    # make up the dirctory in selenium server to store the report for user
    # and return the dirctory name
    logging.debug('in make dir')
    dir_name = os.path.join(config.DEFAULT_DIR, user)
    if not os.path.exists(dir_name):
        output = os.popen('mkdir {}'.format(dir_name))
        logging.debug('create dir, the result is {}'.format(output.read()))
    return dir_name

if __name__ == '__main__':
    # trigger_send_to_ftpserver(HOSTNAME)
    # set_environment(hostname='9.112.56.150')

    from downloader import MyRequest

    request = {}

    r = MyRequest(request)
    r.dirname = os.path.curdir
    send_to_sftpserver(r, r.dirname)