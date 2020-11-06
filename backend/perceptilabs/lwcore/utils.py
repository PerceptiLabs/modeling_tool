import traceback
import re

from perceptilabs.issues import UserlandError


def format_exception(exception, adjust_by_offset=None):
    """ Format an exception with shifted line numbers due to imports and other not-shown stuff """
    pattern = '  File "<rendered-code.*, line ([0-9]*), in .*'
    
    tb_obj = traceback.TracebackException(
        exception.__class__,
        exception,
        exception.__traceback__
    )
    
    def adjust_line_num(match):
        """ Decreases the line number in a traceback string. Assumes that the line string is in the first match. """
        i1, i2 = match.regs[1]
        line_number = int(match.string[i1:i2]) - adjust_by_offset
        new_string = match.string[0:i1] + str(line_number) + match.string[i2:]
        return new_string

    message = ''
    for counter, line in enumerate(tb_obj.format()):
        if adjust_by_offset is None:
            message += line
        else:
            # The code shown to the user does not include the import statements (and the optional preamble)
            # Therefore, we decrease the traceback line by an offset
            message += re.sub(pattern, adjust_line_num, line)
            
    return message


def exception_to_error(layer_id, layer_type, exception, line_offset=None):
    tb_obj = traceback.TracebackException(
        exception.__class__,
        exception,
        exception.__traceback__
    )
    
    # Get the line number of the last frame of rendered code
    line_no = None
    last_rendered_is_another_layer = True

    for frame in tb_obj.stack:
        if frame.filename.startswith(f"<rendered-code: "):
            line_no = int(frame.lineno)
            last_rendered_is_another_layer = not frame.filename.startswith(f"<rendered-code: {layer_id}")

    if last_rendered_is_another_layer:
        # If the origin of the layer is _another_ rendered layer, then we will not raise an error here.
        # Example: A Dense layer has an error that propagates to the training layer.
        return None
    
    # The executed code is different from the code seen by the user (e.g., imports are not shown).
    # Subtract the unseen part to make sure the error is pointed at the correct line
    if line_no is not None and line_offset is not None:
        line_no -= line_offset
        
    message = format_exception(exception, adjust_by_offset=line_offset)
    error = UserlandError(layer_id, layer_type, line_no, message)
    return error
