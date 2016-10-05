easysmb
============

This library wraps around the pysmb library

.. code-block::

    from easypysmb install EasyPySMB

    # Connect
    e = EasyPySMB(
        'smbserver.example.com',
        domain='example.com',
        username='me',
        password='PassW0rd'
    )

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
