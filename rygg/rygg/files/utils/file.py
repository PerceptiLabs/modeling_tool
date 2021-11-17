import chardet
import itertools

def get_file_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw = file.read(32) # at most 32 bytes are returned
        return chardet.detect(raw)['encoding']

def text_file_lines(path):
    encoding=get_file_encoding(path)
    with open(path, 'r', encoding=encoding, errors='backslashreplace') as reader:
        for line in reader:
            yield line.rstrip("\r\n")


def get_text_lines(file_path, num_rows=4):
    assert num_rows >= 0

    try:
        lines = text_file_lines(file_path)
        subset = itertools.islice(lines, 0, num_rows)
        return list(subset)
    except Exception as err:
        raise Exception('Error when reading file contents')

