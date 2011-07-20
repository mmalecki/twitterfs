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
    
    def __repr__(self):
        return "<inode('%s')>" % self.name
        
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
    def __init__(self, name, mode=0755, getter=None, mapper=None,
                 getter_args=[], getter_kwargs={}):
        inode.__init__(self, name, stat.S_IFDIR | mode)
        self.inodes = { }
        self.getter = getter
        self.getter_args = getter_args
        self.getter_kwargs = getter_kwargs
        self.mapper = mapper
    
    def _get_dynamic_inodes(self):
        """ Basically, my idea is very cool. I think I can even state that it's
            the best idea I've had today.
            
            Each Directory can have regular inodes (surprisingly, stored in
            inodes property). But setting those inodes each time something 
            happens in a directory would be very inconvenient. That's why it's 
            easier to define a getter for a directory. This getter is later 
            called when FUSE wants us to list things in a directory.
            
            Sometimes, getter is not enough (when getter is, say, an API, which
            just returns some arbitrary data). That's when mapper comes in.
            When it's not None, it gets called for every item in list, which
            getter returns. That gives us a great degree of automation.
            
            Cool, ain't it?
        """
        
        if self.getter is not None:
            items = self.getter(*self.getter_args, **self.getter_kwargs)
            return map(self.mapper, items)
        else:
            return [ ]
        # That seems... functional.
    
    def to_stat(self):
        """ Returns Stat object describing our File """
        return Stat(st_mode=self.mode, st_nlink=2)
    
    def readdir(self):
        """ Yields each inode, including special (., ..) and dynamical ones """
        yield Directory("..")
        yield Directory(".", self.mode)
        for inode in self.inodes.itervalues():
            yield inode
        for inode in self._get_dynamic_inodes():
            yield inode
            
