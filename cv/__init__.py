from .cv_reader import CVReaders
from .cv_writer import CVWriter

CVRead = CVReaders
CVWriter = CVWriter


def read_txt(file_name):
    return CVRead(file_name)


def write2rst(person_cv, file_name=None):
    CVWriter(person_cv).write(file_name, markup='rst')


def txt2rst(txt_file, rst_file=None):
    write2rst(read_txt(txt_file), rst_file)


if __name__ == '__main__':
    # p = CVRead('semenov.txt')
    # print('\n=== Print person object ===\n{}'.format(p))
    # w = CVWriter(p)
    # print('\n=== Plain text ===\n')
    #  w.write()
    # print('\n=== RestructuredText ===\n')
    # w.write(markup='rst')
    txt2rst('semenov.txt')
