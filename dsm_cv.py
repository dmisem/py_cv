from cv import txt2rst
from docutils.core import publish_cmdline
import os.path as op
import os

txt = op.join(os.getcwd(), 'dsm', 'dsm.txt')
rst = op.join(os.getcwd(), 'dsm', 'dsm.rst')
html = op.join(os.getcwd(), 'html', 'dsm.html')
txt2rst(txt, rst)
publish_cmdline(writer_name='html', argv=[rst, html])
