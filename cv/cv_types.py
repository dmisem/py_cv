# -*- coding: utf-8 -*-
from datetime import date


class CVList():
    def __init__(self, **kwargs):
        self.items = {}
        self.order = {}
        for (k, v) in kwargs.items():
            self.add_item(k, v)

    def add_item(self, item_name, item_value):
        v = self.__prepare_value(item_value)
        if v:
            l = self.items.get(item_name)
            if l:
                l.extend(v)
            else:
                self.order[item_name] = len(self.items)
                self.items[item_name] = v

    def insert_item(self, item_name, item_value, position):
        self.add_item(item_name, item_value)
        self.replace_item(item_name, position)

    def replace_item(self, item_name, position):
        for (k, v) in [(k, v)
                       for (k, v) in self.order.items() if v >= position]:
            self.order[k] = position if k == item_name else v + 1

    @staticmethod
    def __prepare_value(value):
        if not value:
            return None
        if isinstance(value, list):
            return value
        else:
            return [value]

    def __getitem__(self, key):
        res = None
        for k in self.items:
            if key.lower() == k.lower():
                return k, self.items[k]
            if key.lower() in k.lower():
                res = k, self.items[k]
        if res:
            return res
        raise KeyError(key)

    def __iter__(self):
        return CVListIter(self)

    def __str__(self):
        itms = []
        for (k, v) in self:
            itms.append('%s\n' % k.upper())
            for i in v:
                itms.append(str(i))
        return '\n'.join(itms)

    def get(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            return None


class CVListIter():
    def __init__(self, lo):
        self.order = sorted(lo.order.items(), key=lambda x: x[1])
        self.lo = lo
        self.idx = -1
        self.N = len(self.order)

    def __inter__(self):
        return self

    def __next__(self):
        self.idx += 1
        if self.idx < self.N:
            k = self.order[self.idx][0]
            return k, self.lo.items[k]
        else:
            raise StopIteration

    def next(self):
        return self.__next__()


class CVPerson(CVList):
    def __init__(self, aim, name, lname=None, pname=None, **kwargs):
        self.name = name
        self.lname = lname
        self.pname = pname
        self._aim = aim
        super().__init__(**kwargs)

    @property
    def aim(self):
        return self._aim

    @aim.setter
    def aim(self, value):
        if isinstance(value, str):
            self._aim = [value]
        else:
            self._aim = list(value)

    def add_section(self, name, section):
        self.add_item(name, section)

    @property
    def full_name(self):
        fname = [self.name]
        if self.pname:
            fname.append(self.pname)
        if self.lname:
            fname.append(self.lname)
        return ' '.join(fname)

    def __str__(self):
        frmt = '\n{0}\n{1}\n{2}\n'
        return frmt.format(self.full_name, self.aim, self.__items_str())

    def __items_str(self):
        itms = []
        for (k, v) in self:
            itms.append('\n%s' % k)
            for i in v:
                if isinstance(i, tuple):
                    itms.append('* {0}|{1}'.format(*i))
                else:
                    itms.append(str(i))
        return '\n'.join(itms)


class CVWorkExperience(CVList):
    def __init__(self, company, position, start, end=None,
                 resp=None, tech=None, **kwargs):
        if not (company and position and start):
            txt = 'Wrong work parameters: {0}, {1}'.format(company, position)
            raise CVCVWorkExperienceException(txt)
        self._end = None
        self._start = None
        self.company = company
        self.position = position
        self.start = start
        self.end = end
        super().__init__(**kwargs)
        if resp:
            self.insert_item(
                'Responsibilities and Key Accomplishments', resp, 0)
        if tech:
            self.insert_item('Technologies', tech, 1)

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @start.setter
    def start(self, value):
        v = value if isinstance(value, PartialDate) else PartialDate(value)
        if self._end and v > self._end:
            txt = 'Start date can not be later then end date'
            raise CVCVWorkExperienceException(txt)
        self._start = v

    @end.setter
    def end(self, value):
        if value:
            v = value if isinstance(value, PartialDate) else PartialDate(value)
            if v < self._start:
                txt = 'Start date can not be later then end date'
                raise CVCVWorkExperienceException(txt)
            self._end = v
        else:
            self._end = None

    def __str__(self):
        frm = '{0}\n{1}\n{2}\n{3}\n{4}'
        return frm.format(self.start, self.end, self.company,
                          self.position, self.__items_str())

    def __items_str(self):
        itms = []
        for (k, v) in self:
            itms.append(k)
            itms.extend(['* %s' % i for i in v])
        return '\n'.join(itms)


class CVEducation():
    def __init__(self, start, end, name, dep=None, grad=None):
        self._start = None
        self._end = None
        self.start = start
        self.end = end
        self.name = name if name and name.lower() != 'none' else None
        self.dep = dep if dep and dep.lower() != 'none' else None
        self.grad = grad if grad and grad.lower() != 'none' else None

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @start.setter
    def start(self, value):
        v = value if isinstance(value, PartialDate) else PartialDate(value)
        if self._end and v > self._end:
            txt = 'Start date can not be later then end date'
            raise CVCVWorkExperienceException(txt)
        self._start = v

    @end.setter
    def end(self, value):
        if value:
            if isinstance(value, str) and value.lower() == 'none':
                self.__end = None
            else:
                v = value if isinstance(value, PartialDate) else PartialDate(value)
                if v < self._start:
                    txt = 'Start date can not be later then end date'
                    raise CVCVWorkExperienceException(txt)
                self._end = v
        else:
            self._end = None

    def __str__(self):
        res = (str(self.start), str(self.end) if self.end else 'None',
               self.name if self.name else 'None',
               self.dep if self.dep else 'None',
               self.grad if self.grad else 'None')
        return '{0}\n{1}\n{2}\n{3}\n{4}'.format(*res)


class PartialDate(date):
    def __new__(cls, year_or_date, month=None, day=None):
        if isinstance(year_or_date, date):
            res = super().__new__(cls, year_or_date.year, year_or_date.month,
                                  year_or_date.day)
        elif isinstance(year_or_date, str):
            ymd = [int(itm) for itm in year_or_date.split()]
            ymd += [1] * (3 - len(ymd))
            res = super().__new__(cls, *ymd)
        else:
            __year = int(year_or_date)
            if __year < 1000:
                __year += 2000
            if day and month:
                res = super().__new__(cls, __year, int(month), int(day))
            elif month:
                res = super().__new__(cls, __year, int(month), 1)
            else:
                res = super().__new__(cls, __year, 1, 1)
        return res

    def __init__(self, year_or_date, month=None, day=None):
        if isinstance(year_or_date, str):
            ymd = year_or_date.split()
            self.period = ['y', 'm', 'd'][len(ymd) - 1]
        else:
            isd = isinstance(year_or_date, date) or (day and month)
            self.period = 'd' if isd else 'm' if month else 'y'

    def __str__(self):
        if self.period == 'd':
            return self.strftime('%Y %m %d')
        else:
            if self.period == 'm':
                m = date(self.year, self.month, 1)
                return m.strftime('%Y %m')
            else:
                return str(self.year)

    def strf(self):
        if self.period == 'd':
            return self.strftime('%x')
        else:
            if self.period == 'm':
                m = date(1900, self.month, 1).strftime('%B')
                return '%s %s' % (m, self.year)
            else:
                return str(self.year)


class CVException(Exception):
    pass


class CVCVWorkExperienceException(CVException):
    pass


class CVPersonException(CVException):
    pass
