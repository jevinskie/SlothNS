#!/usr/bin/env python
import virtualenv
import inspect
import os
import stat

def after_install(options, home_dir):
    subprocess.check_call([join(home_dir, 'bin', 'pip'),
                            'install', 'construct', 'twisted'])

src = ''.join(inspect.getsourcelines(after_install)[0])

script = virtualenv.create_bootstrap_script(src)
with open('virtenv-bootstrap.py', 'w') as f:
    f.write(script)
    os.fchmod(f.fileno(), stat.S_IRWXU |
                          stat.S_IRGRP | stat.S_IXGRP |
                          stat.S_IROTH | stat.S_IXOTH)

