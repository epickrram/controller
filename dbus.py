import subprocess
import StringIO
import tempfile
import re

FIRST_RESPONSE_VALUE_REGEX = re.compile('.*\n[ ]+[^ ]+ ([^ ]+).*', re.MULTILINE)

class Dbus(object):
    def get_first_response_value(self, std_out):
        match = FIRST_RESPONSE_VALUE_REGEX.search(std_out)
        if match is not None:
            return match.group(1)

        raise ValueError('Could not find first response value in : ' + std_out)

    def send(self, args):
        process_result = self.execute_process(args)
        self.validate_response_code(process_result, args)

    def send_and_get_response(self, args):
        process_result = self.execute_process(args)
        self.validate_response_code(process_result, args)
        return process_result.std_out
        
    def execute_process(self, args):
        stdout_capture = tempfile.TemporaryFile()
        stderr_capture = tempfile.TemporaryFile()
        response_code = subprocess.call(args, stdout=stdout_capture, stderr=stderr_capture)
        stdout_capture.seek(0)
        stderr_capture.seek(0)
        return ProcessResult(response_code, stdout_capture.read(), stderr_capture.read())

    def validate_response_code(self, process_result, args):
        if int(process_result.response_code) is not 0:
            raise ValueError('Process exited with code {0}, args: {1}'.format(process_result.response_code, str(args)))
        

class ProcessResult(object):
    def __init__(self, response_code, std_out, std_err):
        self.response_code = response_code
        self.std_out = std_out
        self.std_err = std_err

if __name__ == '__main__':
    dbus = Dbus()
    cmd = "dbus-send --type=method_call --print-reply --dest=com.gnome.mplayer / com.gnome.mplayer.GetFullScreen"
    cmd = ['dbus-send','/','com.gnome.mplayer.Open','string:/home/mark/dev/controller/foo/music 2/2013-09-26-180454.ogg']
    result = dbus.execute_process(cmd)
    print 'response code: {0}'.format(result.response_code)
    print 'stdout: {0}'.format(result.std_out)
    print 'stderr: {0}'.format(result.std_err)
