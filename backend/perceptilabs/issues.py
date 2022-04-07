import os
import uuid
import queue
import inspect
import traceback
import logging

from perceptilabs.utils import add_line_numbering

ISSUE_LOG_FORMAT = "%(asctime)s:%(lineno)d - %(message)s"


def traceback_from_exception(exception):
    tb_obj = traceback.TracebackException(
        exception.__class__, exception, exception.__traceback__
    )
    text = "".join(tb_obj.format())
    return text


class UserlandError:
    def __init__(self, layer_id, layer_type, line_number, message, code=None):
        self.layer_id = layer_id
        self.layer_type = layer_type
        self.line_number = line_number or 0
        self.message = message
        self.code = code

    def format(self, with_code=False):
        text = f"Userland error in layer {self.layer_id} [{self.layer_type}]. "

        if self.line_number is not None:
            text += f"Line: {self.line_number}"

        if with_code and self.code is not None:
            text += "\n" + add_line_numbering(self.code)

        text += "\n" + self.message
        return text

    def __repr__(self):
        return self.format()
