#!/usr/bin/env python

import env
import os
import sys
from subprocess import Popen, call
from tempfile import TemporaryFile

#from run_unit_tests import run_unit_tests

ROBOT_ARGS = [
    '--doc', 'YamlVariablesOutput',
    '--outputdir', '%(outdir)s',
    '--escape', 'space:SP',
    '--report', 'none',
    '--log', 'none',
    '--loglevel', 'DEBUG',
    '--pythonpath', '%(pythonpath)s',
]
REBOT_ARGS = [
    '--outputdir', '%(outdir)s',
    '--name', 'YamlVariablesOutput',
    '--escape', 'space:SP',
    '--critical', 'regression',
    '--noncritical', 'inprogress',
]
ARG_VALUES = {'outdir': env.RESULTS_DIR, 'pythonpath': env.SRC_DIR}


def acceptance_tests(interpreter, args):
    #ARG_VALUES['browser'] = browser.replace('*', '')
    runner = {'python': 'pybot', 'jython': 'jybot', 'ipy': 'ipybot'}[interpreter]
    if os.sep == '\\':
        runner += '.bat'
    execute_tests(runner, args)
    return process_output(args)


def execute_tests(runner, args):
    if not os.path.exists(env.RESULTS_DIR):
        os.mkdir(env.RESULTS_DIR)
    #command = [runner] + [arg % ARG_VALUES for arg in ROBOT_ARGS] + args + [env.ACCEPTANCE_TEST_DIR]
    tmp1 = [arg % ARG_VALUES for arg in ROBOT_ARGS] + args + [env.ACCEPTANCE_TEST_DIR]
    print ' '.join(tmp1)
    #command = [runner]
    #command.append(' '.join(tmp1))
    #command = [' '.join(tmp1)]
    #command.append(runner)
    print ''
    print 'Starting test execution with command:\n' + ' '.join(command)
    syslog = os.path.join(env.RESULTS_DIR, 'syslog.txt')
    print os.sep
    print command
    #call(command, shell=os.sep=='\\', env=dict(os.environ, ROBOT_SYSLOG_FILE=syslog))
    call(command, shell=True, env=dict(os.environ, ROBOT_SYSLOG_FILE=syslog))
    #call(command, env=dict(os.environ))
    #print ' '.join(command)
    #call('pybot', '--doc YamlVariablesOutput --outputdir /Users/julesbarnes/workspace/git/robotframework-yamlvariableslibrary/YamlVariablesLibrary/tests/results --escape space:SP --report none --log none --loglevel DEBUG --pythonpath /Users/julesbarnes/workspace/git/robotframework-yamlvariableslibrary/YamlVariablesLibrary/tests/.. --loglevel DEBUG /Users/julesbarnes/workspace/git/robotframework-yamlvariableslibrary/YamlVariablesLibrary/tests/acceptance')

def process_output(args):
    print
    if _has_robot_27():
        call(['python', os.path.join(env.RESOURCES_DIR, 'statuschecker.py'),
             os.path.join(env.RESULTS_DIR, 'output.xml')])
    rebot = 'rebot' if os.sep == '/' else 'rebot.bat'
    rebot_cmd = [rebot] + [ arg % ARG_VALUES for arg in REBOT_ARGS ] + args + \
                [os.path.join(ARG_VALUES['outdir'], 'output.xml') ]
    rc = call(rebot_cmd, env=os.environ)
    if rc == 0:
        print 'All critical tests passed'
    else:
        print '%d critical test%s failed' % (rc, 's' if rc != 1 else '')
    return rc

def _has_robot_27():
    try:
        from robot.result import ExecutionResult
    except:
        return False
    return True

def _exit(rc):
    sys.exit(rc)

def _help():
    print 'Usage:  python run_tests.py python|jython browser [options]'
    print
    print 'See README.txt for details.'
    return 255

#def _run_unit_tests():
#    print 'Running unit tests'
#    failures = run_unit_tests()
#    if failures != 0:
#        print '\n%d unit tests failed - not running acceptance tests!' % failures
#    else:
#        print 'All unit tests passed'
#    return failures


if __name__ ==  '__main__':
    if not len(sys.argv) > 1:
        _exit(_help())
#    unit_failures = _run_unit_tests()
#    if unit_failures:
#        _exit(unit_failures)
    interpreter = sys.argv[1]
 #   browser = sys.argv[2].lower()
    args = sys.argv[2:]
    _exit(acceptance_tests(interpreter, args))