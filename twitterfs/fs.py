import fuse
import errno
import stat
import logging
import inodes

fuse.fuse_python_api = (0, 2)

class TwitterFS(fuse.Fuse):
    def __init__(self, *args, **kwargs):
        logging.debug("TwitterFS.__init__(self, %s, %s)" % (repr(args), repr(kwargs))) 
        fuse.Fuse.__init__(self, *args, **kwargs)
        logging.debug("Fuse.__init__'ialized") 
    
    def fsinit(self):
        logging.debug("self.fuse_args = %s" % self.fuse_args)
        logging.info('Initializing TwitterFS at ' + self.mountpoint)
    
    def getattr(self, path):
        logging.debug("self.getattr(self, %s)" % repr(path))
        return inodes.Directory("/", 0755).to_stat()
    
    def readdir(self, path, offset):
        logging.debug("self.readdir(self, %s, %s)" % (repr(path), repr(offset)))
        for inode in inodes.Directory("/", 0755).readdir():
            yield inode.to_direntry()
        
