from . command import Command
from .. util import rrgit_error, data_size, TIMESTAMP_FMT
from .. log import *
from . file_ops import *

import os
from datetime import datetime
import glob

class Pull(Command):
    @staticmethod
    def add_parser(sp):
        p = sp.add_parser('pull', 
            help='Pull changes from RRF/Duet device')
        p.add_argument('--force', '-f', action='store_true', default=False)
        
    def __init__(self, cfg, args):
        super().__init__(cfg, args)
        self.connect()
        
    def run(self):
        report = build_status_report(self.dwa, self.cfg, self.directories)
        
        ro = report['remote_only']
        
        rn = list(report['remote_newer'].keys())
        rn.sort()
        ln = list(report['local_newer'].keys())
        ln.sort()
        ds = list(report['diff_size'].keys())
        ds.sort()
        
        if not self.args.force and (len(ln) > 0 or len(ds) > 0) :
            if len(ln) > 0:
                error('The following files have newer changes locally.')
                for path in ln:
                    info(f'- {path}')
            if len(ds) > 0:
                error('The following files differ only in size.')
                for path in ds:
                    info(f'- {path}')
            error('Use -f to force overwritting local copies.')
            return
            
        if len(ro) > 0 or len(rn) > 0 or len(ln) > 0 or len(ds) > 0:
            status('Fetching files from remote...')
            for path in ro:
                status(f'- {path}')
                report['remote_files'][path].pullFile(self.dwa, self.cfg.dir)
    
            for path, fo in report["remote_newer"].items():
                status(f'- {path}')
                fo.pullFile(self.dwa, self.cfg.dir)
                
            for path in ln:
                fo = report['remote_files'][path]
                status(f'- {path}')
                fo.pullFile(self.dwa, self.cfg.dir)
                
            for path, fo in report["diff_size"].items():
                status(f'- {path}')
                rfo = fo[0]
                rfo.pullFile(self.dwa, self.cfg.dir)
        else:
            success('No changes detected')
        