# easysmb

![PyPI](https://img.shields.io/pypi/v/easypysmb)
![PyPI - Downloads](https://img.shields.io/pypi/dm/easypysmb)
![PyPI - License](https://img.shields.io/pypi/l/easypysmb)
![Python Lint](https://github.com/pschmitt/easypysmb/workflows/Python%20Lint/badge.svg)

This library eases the use of pysmb by providing simple functions to do basic stuff.

```python
from easypysmb import EasyPySMB

# Connect
e = EasyPySMB(
    'smbserver.example.com',
    domain='example.com',
    username='me',
    password='PassW0rd'
)

# List files
e.ls('share1/')

# Store files
e.store_file('/tmp/test.txt', 'share1/test.txt')

# Retrieve files
f = e.retrieve_file('share1/text.txt')

# Backup files
e.backup_file('share1/text.txt', 'share2/test.backup.txt')

# mkdir -p
e.mkdir('share1/dir1/dir2/dir3')

# Terminate connection
e.close()
```
