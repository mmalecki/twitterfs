import fuse
import errno
import stat
import logging
import os

from inodes import Directory
from utils import repr_

fuse.fuse_python_api = (0, 2)

class TwitterFS(fuse.Fuse):
    def __init__(self, *args, **kwargs):
        logging.debug("%s.__init__(self, %s, %s)" % repr_(self, args, kwargs)) 
        fuse.Fuse.__init__(self, *args, **kwargs)
        logging.debug("Fuse.__init__'ialized")
        
        self.main_dir = Directory("/", 0755)
        
        self.main_dir.inodes = { "followers" : Directory("followers", 0555),
                                 "following" : Directory("following"),
                                 "me" : Directory("me") }
                                 
    
    def fsinit(self):
        logging.debug("%s.fuse_args = %s" % repr_(self, self.fuse_args))
        logging.info('Initializing TwitterFS at ' + self.mountpoint)
    
    def getattr(self, path):
        logging.debug("%s.getattr(self, %s)" % repr_(self, path))
        inode = self.find_inode(self.main_dir, path)
        return inode.to_stat() if inode else -errno.ENOENT
    
    def find_inode(self, inode, path):
        logging.debug("%s.find_inode(self, %s, %s)" % repr_(self, inode, path))
        
        path = path.lstrip("/")
        if path == "":
            return inode
        else:
            sep_index = path.find(os.sep)
            if sep_index == -1:
                return inode.inodes.get(path)
            else:
                name = path[:sep_index]
                if name in inode.inodes:
                    path = path[sep_index + 1:]
                    return self.find_inode(inode.inodes[name], path)
    
    def readdir(self, path, offset):
        logging.debug("%s.readdir(self, %s, %s)" % repr_(self, path, offset))
        
        inode = self.find_inode(self.main_dir, path)
        if inode:
            return map(lambda i: i.to_direntry(), inode.readdir())
        else:
            return -errno.ENOENT
            
        
