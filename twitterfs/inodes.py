import os
import stat
import fuse
import logging

class Stat(fuse.Stat):
    def __init__(self, st_atime=0, st_ctime=0, st_dev=0, st_gid=os.getgid(),
                 st_ino=0, st_mode=0, st_mtime=0, st_nlink=1, st_size=0,
                 st_uid=os.getuid()):
        fuse.Stat.__init__(self)
        self.st_atime = st_atime
        self.st_ctime = st_ctime
        self.st_dev = st_dev
        self.st_gid = st_gid
        self.st_ino = st_ino
        self.st_mode = st_mode
        self.st_mtime = st_mtime
        self.st_nlink = st_nlink
        self.st_size = st_size
        self.st_uid = os.getuid()

class inode(object):
    def __init__(self, name, mode=0755):
        self.name = name
        self.mode = mode
        
    def to_direntry(self):
        """ Returns corresponding Direntry object, used by FUSE to list inodes 
            in directories 
        """
        d = fuse.Direntry(self.name)
        d.mode = self.mode
        return d
    
    def to_stat(self):
        """ Returns Stat object, used by FUSE to describe files on filesystem """
        return Stat(st_mode=self.mode)


class File(inode):
    """ Represents a file on our filesystem """
    def __init__(self, name, mode=0755):
        inode.__init__(self, name, stat.S_IFREG | mode)
    
    
class Directory(inode):
    def __init__(self, name, mode=0755):
        inode.__init__(self, name, stat.S_IFDIR | mode)
        self.inodes = { }
    
    def to_stat(self):
        """ Returns Stat object describing our File """
        return Stat(st_mode=self.mode, st_nlink=2)
    
    def readdir(self):
        """ Yields each inode, including special ones (., ..) """
        yield Directory("..")
        yield Directory(".", self.mode)
        for inode in self.inodes:
            yield inode
