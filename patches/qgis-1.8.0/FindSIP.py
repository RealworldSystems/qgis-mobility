# FindSIP.py
#
# Copyright (c) 2007, Simon Edwards <simon@simonzone.com>
# Redistribution and use is allowed according to the terms of the BSD license.
# For details see the accompanying COPYING-CMAKE-SCRIPTS file.

import sys
import os
import sipconfig

sipcfg = sipconfig.Configuration()
print("sip_version:%06.0x" % sipcfg.sip_version)
print("sip_version_num:%d" % sipcfg.sip_version)
print("sip_version_str:%s" % sipcfg.sip_version_str)
print("sip_bin:%s" % sipcfg.sip_bin)

replacers = {"default_sip_dir": sipcfg.default_sip_dir,
             "sip_inc_dir": sipcfg.sip_inc_dir,
             "sip_mod_dir": sipcfg.sip_mod_dir}

for key in replacers:
    v = replacers[key]
    replacers[key] = v.replace('hostpython', os.path.join('build', 'Python-2.7.2'))

print("default_sip_dir:%s" % replacers['default_sip_dir'])
print("sip_inc_dir:%s" % replacers['sip_inc_dir'])
print("sip_mod_dir:%s" % replacers['sip_mod_dir'])
