from .cv_types import CVPerson, CVException
from .cv_types import CVWorkExperience, CVEducation


class CVReader():
    def __new__(cls, file_name):
        cls.__file_name = file_name
        cls.read_source()
        return CVPerson(cls.aim, cls.name, cls.lname, cls.pname,
                        **cls.sections)

    @classmethod
    def read_source(cls):
        def write_section():
            sf = cls.read_FieldList
            sl = section.lower()
            if sl == 'workexperience':
                sn, sf = 'Summary of Work Experience', cls.read_WorkExperiance
            elif sl in 'foreign languages':
                sn = 'Foreign Languages Skills'
            elif (sl in 'education') or (sl in 'academic'):
                sn, sf = 'Academic records', cls.read_Education
            else:
                sn = section
            cls.sections[sn] = sf(slist)

        with open(cls.__file_name) as f:
            fn = next(f).split()
            cls.name = fn[0]
            cls.lname = fn[-1] if len(fn) > 1 else None
            cls.pname = ' '.join(fn[1:-1]) if len(fn) > 2 else None
            cls.aim = next(f).strip()
            cls.sections = {}
            section = ''
            slist = []
            for l in (x.strip() for x in f.readlines()):
                if l:
                    if section:
                        slist.append(l)
                    else:
                        section = l
                else:
                    write_section()
                    section = ''
                    slist = []
            write_section()

    @staticmethod
    def read_FieldList(slist):
        fld = 0
        if len(slist) == 0:
            return []
        if not slist[0].strip().startswith('* '):
            return ['\n'.join(slist)]
        res = []
        for l in slist:
            ll = l[2:] if l.startswith('* ') else l
            p = ll.split('|', 1)
            if len(p) >= 2:
                if len(p[1]) < 150:
                    fld = 1 if fld < 2 else 2
                else:
                    fld = 2
                res.append((p[0].strip(), p[1].strip()))
            else:
                res.append(('', ll))
        return [r + (fld,) for r in res]

    @staticmethod
    def read_WorkExperiance(slist):
        idx = 0
        res = []
        itms = {}
        comp, pos, dstart, dend = None, None, None, None
        section = ''
        for l in slist:
            if idx != 1 and '1900' < l[:4] < '2100':
                if idx > 2:
                    we = CVWorkExperience(comp, pos, dstart, dend, **itms)
                    res.append(we)
                idx = 1
                dstart = l
            else:
                if idx == 1:
                    dend = l if l and l.lower() != 'none' else None
                elif idx == 2:
                    comp = l
                elif idx == 3:
                    pos = l
                elif idx == 4:
                    section = l
                    itms[section] = []
                else:
                    if l.startswith('* '):
                        itms[section].append(l[2:].strip())
                    else:
                        section = l
                        itms[section] = []
                idx += 1
        if idx > 2:
            res.append(CVWorkExperience(comp, pos, dstart, dend, **itms))
        return res

    @staticmethod
    def read_Education(slist):
        def split_edulist(lst):
            for i in range(3, len(lst)):
                if len(lst[i]) > 3 and '1900' < lst[i] < '2100':
                    ed = [CVEducation(*lst[:i])]
                    ed.extend(split_edulist(lst[i:]))
                    return ed
            return [CVEducation(*lst)]
        return split_edulist(slist)


class CVReaders():
    def __new__(cls, file_name, reader_type=None):
        if hasattr(cls, 'readers'):
            rt = reader_type if reader_type else file_name.rsplit('.', 1)[-1]
            return cls.__get_reader(rt)(file_name)
        else:
            raise CVReadExcetion('No readers registered')

    @classmethod
    def __get_reader(cls, reader_type):
        rt = reader_type if reader_type else 'text'
        return cls.readers.get(rt)

    @classmethod
    def register(cls, rt_names, r_type):
        rts = [rt_names] if isinstance(rt_names, str) else rt_names
        for rt in rts:
            if hasattr(cls, 'readers'):
                cls.readers[rt] = r_type
            else:
                cls.readers = {rt: r_type}


class CVReadExcetion(CVException):
    pass


CVReaders.register(['text', 'txt'], CVReader)


if __name__ == '__main__':
    p = CVReader('semenov.txt')
    print(p)
