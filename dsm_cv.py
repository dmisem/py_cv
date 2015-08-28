from cv import txt2rst
from docutils.core import publish_cmdline
import os.path as op
import os

fname = op.join(os.getcwd(), 'dsm', 'dsm')
names = dict(
    txt='%s.txt' % fname,
    rst='%s.rst' % fname,
    html='%s.html' % fname,
)
txt2rst(names['txt'], names['rst'])
publish_cmdline(writer_name='html', argv=[names['rst'], names['html']])
