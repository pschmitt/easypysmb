#/usr/bin/python
# coding: utf-8


from nmb.NetBIOS import NetBIOS
from smb.SMBConnection import SMBConnection
import logging
import re
import tempfile
import os


logging.basicConfig()
logger = logging.getLogger(__name__)
logging.getLogger('SMB.SMBConnection').setLevel(logging.WARNING)


def get_netbios_name(hostname):
    if hostname in ['127.0.0.1', 'localhost']:
        return 'localhost'
    n = NetBIOS()
    return n.queryIPForName(hostname)[0]


class EasyPySMB():

    def __init__(self, hostname, username='GUEST', password=None, domain=None,
                client_name=None, port=139, share_name=None, file_path=None):
        if hostname.startswith('smb://'):
            regex = 'smb://(((.+);)?(.+):(.+)@)?([^/]+)(/([^/]+))?(/.*)?'
            m = re.match(regex, hostname)
            if not m:
                raise ValueError('Could not decompose smb path. The regex failed.')
            domain = m.group(3) if m.group(3) else ''
            username = m.group(4) if m.group(4) else 'GUEST'
            password = m.group(5) if m.group(5) else ''
            hostname = m.group(6)
            share_name = m.group(8)
            file_path = m.group(9)
            logger.debug(
                'Domain: {} Username: {} Password: {} Server: {} Share: {} ' \
                'File Path: {}'.format(
                    domain, username, password, hostname, share_name, file_path
                )
            )
        if not client_name:
            client_name = __name__
        self.conn = SMBConnection(
            domain=domain,
            username=username,
            password=password,
            my_name=client_name,
            remote_name=get_netbios_name(hostname),
            use_ntlm_v2=True
        )
        if not self.conn.connect(hostname, port):
            logger.error(
                'Could not connnect to SMB server. Please verify the '\
                'connection data'
            )
        # tmpdir is a temp dir that holds the transfered files by default
        self.tmpdir = tempfile.mkdtemp(prefix='easypysmb_')
        self.share_name = share_name
        self.file_path = file_path
        if self.share_name:
            available_shares = [x.lower() for x in self.list_shares()]
            if self.share_name.lower() not in available_shares:
                logger.warning(
                    'Share {} does not exist on the server'.format(self.share_name)
                )
        dir_content = [x.filename for x in self.ls(os.path.dirname(self.file_path))]
        if os.path.basename(self.file_path) not in dir_content:
            logger.warning(
                'File {} does not exist on the server'.format(self.file_path)
            )

    def __decompose_smb_path(self, path):
        '''
        Get the share name and filepath
        '''
        split_path = path.split('/')
        return split_path[0], '/'.join(split_path[1:])

    def __guess_share_name(self, path, share_name=None):
        if share_name:
            return share_name, path
        available_shares = [x.lower() for x in self.list_shares()]
        if not share_name:
            first_dir = path.split('/')[0].lower()
            if first_dir in available_shares:
                logger.info(
                    'Path {} matches share name {}'.format(path, first_dir)
                )
                share_name, path = self.__decompose_smb_path(path)
            elif self.share_name:
                share_name = self.share_name
        return share_name, path

    def close(self):
        self.conn.close()

    def list_shares(self):
        return [x.name for x in self.conn.listShares()]

    def store_file(self, file_obj, dest_path, share_name=None, retries=3):
        share_name, dest_path = self.__guess_share_name(dest_path, share_name)
        if type(file_obj) is str or type(file_obj) is str:
            file_obj = open(file_obj)
        for r in range(1, retries + 1):
            try:
                return self.conn.storeFile(
                    share_name,
                    dest_path,
                    file_obj
                )
            except Exception as e:
                logger.error(
                    'Attempt {}/{} to store file on SMB share failed:\n{}'.format(
                        r, retries, e
                    )
                )

    def retrieve_file(self, dest_path=None, file_obj=None, share_name=None):
        if not dest_path:
            dest_path = self.file_path
        assert dest_path, 'Destination path is unset'
        share_name, dest_path = self.__guess_share_name(dest_path, share_name)
        if not file_obj:
            file_obj = open(
                os.path.join(self.tmpdir, os.path.basename(dest_path)),
                'w+b'
            )
            # file_obj = tempfile.NamedTemporaryFile(
            #     prefix='py_',
            #     suffix=os.path.basename(dest_path),
            #     dir=self.tmpdir,
            #     delete=False
            # )
        elif type(file_obj) is str or type(file_obj) is str:
            file_obj = open(file_obj, 'wb')
        bytes_transfered = self.conn.retrieveFile(share_name, dest_path, file_obj)
        logger.info('Transfered {} bytes'.format(bytes_transfered))
        file_obj.close() # write file
        file_obj = open(file_obj.name)
        return file_obj

    def backup_file(self, backup_file_path, file_path=None, share_name=None,
                    backup_share_name=None):
        if not file_path:
            file_path = self.file_path
        assert file_path, 'Destination path is unset'
        share_name, file_path = self.__guess_share_name(file_path, share_name)
        backup_share_name, backup_file_path = self.__guess_share_name(
            backup_file_path, backup_share_name
        )
        logger.info(
            'Back up file {}:{} to {}:{}'.format(
                share_name, file_path, backup_share_name, backup_file_path
            )
        )
        tmp_file = tempfile.NamedTemporaryFile(
            suffix=os.path.splitext(file_path)[1], delete=False
        )
        tmp_file = self.retrieve_file(
            share_name=share_name, dest_path=file_path, file_obj=tmp_file
        )
        res = self.store_file(
            share_name=backup_share_name,
            dest_path=backup_file_path,
            file_obj=tmp_file
        )
        # Clean up
        os.remove(tmp_file.name)
        return res

    def mkdir(self, dir_path, share_name=None):
        share_name, dir_path = self.__guess_share_name(dir_path, share_name)
        # Recursively create directories, just like mkdir -p does
        directories = dir_path.split('/')
        tmp_path = ''
        for d in directories:
            dir_content = self.conn.listPath(share_name, tmp_path)
            if d not in [x.filename for x in dir_content if x.isDirectory]:
                logger.info('Directory {} is missing. Create it'.format(d))
                self.conn.createDirectory(share_name, '{}/{}'.format(tmp_path, d))
            tmp_path += '/{}'.format(d)

    def rm(self, file_path, share_name=None):
        if not share_name:
            if self.share_name:
                share_name = self.share_name
            else:
                share_name, file_path = self.__decompose_smb_path(file_path)
        return self.conn.deleteFiles(share_name, file_path)

    def ls(self, path='', share_name=None):
        if not share_name:
            if self.share_name:
                share_name = self.share_name
            else:
                share_name, path = self.__decompose_smb_path(path)
        logger.info('List files in {}:{}'.format(share_name, path))
        return self.conn.listPath(share_name, path=path)
