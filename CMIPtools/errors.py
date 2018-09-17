import traceback
import sys

TRACEBACK_TEMPLATE = '''Traceback (most recent call last): 
      File "%(filename)s", line %(lineno)s, in %(name)s
      %(type)s: %(message)s\n'''

def handle(err):
    etype = sys.exc_info()[0]
    evalue = sys.exc_info()[1]
    etraceback = sys.exc_info()[2]
    traceback_details = {
        'filename': etraceback.tb_frame.f_code.co_filename,
        'lineno': etraceback.tb_lineno,
        'name': etraceback.tb_frame.f_code.co_name,
        'type': etype.__name__,
        'message': evalue.message,
    }
    print
    print traceback.format_exc()
    print
    print TRACEBACK_TEMPLATE % traceback_details
    print
    raise(err)
