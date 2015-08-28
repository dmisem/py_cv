# -*- coding: utf-8 -*-
from contextlib import contextmanager
import sys
from . import cv_types as cv


@contextmanager
def fwopen(filename=None):
    f = open(filename, 'w') if filename else sys.stdout
    yield f
    if filename:
        f.close()


class CVML():
    def __new__(cls, file_name=None, markup=None):
        if not hasattr(cls, '_CVML__ML') or len(cls.__ML) == 0:
            raise CVMLException('Not found markup formatter.')
        if markup:
            if isinstance(markup, CVML):
                ml = markup()
            else:
                ml = cls.__ML.get(markup.lower())
        elif file_name:
            ml = cls.__ML.get(file_name.rsplit('.', 1)[-1].lower())
        else:
            ml = cls
        if ml:
            return super().__new__(ml)
        else:
            raise CVWriterException('Markup not fount')

    @classmethod
    def register(cls, names, markup):
        if not issubclass(markup, CVML):
            return
        if not hasattr(cls, '__ML'):
            cls.__ML = {}
        if isinstance(names, str):
            nms = [names.lower()]
        else:
            nms = [n.lower() for n in names]
        for n in nms:
            cls.__ML[n] = markup

    def __getattr__(self, name):
        wlist = ['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'p']
        if name.lower() in wlist:
            return self.__write
        else:
            raise AttributeError(name)

    def __write(self, text):
        return '%s\n' % text

    def ul(self, items):
        if isinstance(items, str):
            return '- {0}\n'.format(items)
        else:
            return ''.join([self.ul(i) for i in items])

    def fl(self, items):
        if isinstance(items, str):
            return self.ul(items)
        else:
            if isinstance(items, str) or len(items) < 2:
                return self.ul(items)
            else:
                if items[0]:
                    return '- {0} | {1}'.format(items[0], items[1])
                else:
                    return '%s\n' % items[1]

    def fd(self, text):
        return self.fl(text)


class CVReST(CVML):
    def __str__(self):
        return 'RestructuredText'

    def __getattr__(self, name):
        hl = dict(h1='=', h2='-', h3='~', h4='"', h5="'", h6='`')
        if name in hl:
            return self.__h(hl[name])
        else:
            raise AttributeError(name)

    def title(self, text):
        s = '#' * len(text)
        return '{0}\n{1}\n{0}\n\n'.format(s, text)

    def __h(self, hx):
        def __hx(text):
            s = hx * len(text)
            return '{0}\n{1}\n\n'.format(text, s)
        return __hx

    def ul(self, items, idx=0):
        s = ['-', '*', '+'][idx % 3]
        if isinstance(items, str):
            return '{1} {0}\n'.format(items, s)
        else:
            return '{0}\n'.format(''.join([self.ul(i, idx+1) for i in items]))

    def fl(self, items):
        if isinstance(items, str):
            return self.ul(items)
        else:
            if isinstance(items, str) or len(items) < 2:
                return self.ul(items)
            else:
                if items[0]:
                    return self.ul('**{0}** {1}'.format(*items))
                else:
                    return self.ul('%s' % items[1])

    def fd(self, item):
        return ':{0}: {1}\n'.format(*item)

    def strong(self, text):
        return '**{0}**\n\n'.format(text)

    def p(self, text):
        return '{0}\n\n'.format(text)


class CVWriter():
    def __init__(self, person):
        self.p = person

    def write(self, file_name=None, markup=None):
        ml = CVML(file_name, markup)
        lwrote = []
        with fwopen(file_name) as f:
            f.write(ml.title(self.p.full_name))
            f.write(ml.h1(self.p.aim))
            lwrote.append(self.__write_NamedFileds('summary', f, ml))
            lwrote.append(self.__write_WorkExcperience(f, ml))
            lwrote.append(self.__write_Education(f, ml))
            lwrote.append(self.__write_NamedFileds('lang', f, ml))

            for i in [s for s in self.p if s[0] not in lwrote]:
                self.__write_FieldList(f, ml, i)

    def __write_Education(self, f, ml):
        ed = self.p.get('education') or self.p.get('academic')
        if ed:
            f.write(ml.h2('\n%s' % ed[0]))
            for e in ed[1]:
                if e.end:
                    s1 = '{0} - {1}. {2}'.format(e.start, e.end, e.name)
                else:
                    s1 = '{0}. {1}'.format(e.start, e.name)
                f.write(ml.strong(s1))
                if e.dep:
                    f.write(ml.p(e.dep))
                if e.grad:
                    f.write(ml.p('Graduate: {0}'.format(e.grad)))
            return ed[0]
        return None

    def __write_WorkExcperience(self, f, ml):
        we = self.p['experience']
        f.write(ml.h2('\n%s' % we[0]))
        for w in we[1]:
            f.write(ml.h3('{0} -- {1}'.format(w.start.strf(), w.end.strf()
                                              if w.end else 'now')))
            f.write(ml.h4(w.company))
            f.write(ml.h4(w.position))
            for (k, v) in w:
                f.write(ml.h5('%s:' % k))
                f.write(ml.ul(v))
        return we[0]

    def __write_FieldList(self, f, ml, itm):
        f.write(ml.h2('\n%s' % itm[0]))
        for s in itm[1]:
            if isinstance(s, str):
                f.write('%s\n' % s)
            else:
                try:
                    ff = [ml.ul, ml.fd, ml.fl][s[2]]
                except Exception:
                    ff = ml.ul
                f.write('%s' % ff(s))
        return itm[0]

    def __write_NamedFileds(self, name, f, ml):
        itm = self.p[name]
        return self.__write_FieldList(f, ml, itm)


class CVMLException(cv.CVException):
    pass


class CVWriterException(cv.CVException):
    pass


CVML.register(['rest', 'rst'], CVReST)
