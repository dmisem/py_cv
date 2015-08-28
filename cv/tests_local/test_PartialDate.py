import sys
import os.path as op
up_dir = op.dirname(op.dirname(op.abspath(__file__)))
sys.path.insert(0, up_dir)
import cv_types as cv

from datetime import date
from nose.tools import raises


y = 2015
m = 12
d = 31


def test_fulldate():
    pd = cv.PartialDate(y, m, d)
    assert (pd.strf() == date(y, m, d).strftime('%x')
            and pd.period == 'd'
            and str(pd) == '{} {} {}'.format(y, m, d))


def test_month_year():
    pd = cv.PartialDate(y, m)
    assert (pd.strf() == '{} {}'.format(date(y, m, d).strftime('%B'), y)
            and pd.period == 'm'
            and str(pd) == '{} {}'.format(y, m))


def test_year():
    pd = cv.PartialDate(y)
    assert pd.strf() == str(y) and pd.period == 'y' and str(pd) == str(y)


def test_date():
    td = date(y, m, d)
    pd = cv.PartialDate(td)
    assert (pd.strf() == td.strftime('%x')
            and pd.period == 'd'
            and str(pd) == '{} {} {}'.format(y, m, d))


@raises(ValueError)
def test_wrong_date():
    cv.PartialDate(y, 2, d)


@raises(ValueError)
def test_wrong_month():
    cv.PartialDate(y, 13)


if __name__ == '__main__':
    import nose
    nose.main(argv=sys.argv + ['-vv'])
