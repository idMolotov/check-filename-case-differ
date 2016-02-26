import os
import platform
import argparse
import subprocess

parser = argparse.ArgumentParser(
    description='Checking camelCase directory/filenames difference between git HEAD and local.')
parser.add_argument('--basedir',
                    default='/tmp',
                    type=str,
                    help='directory where is repository HOME')

args = parser.parse_args()
BASE_DIR = args.basedir

# print(platform.system()) # TODO check on Win filesystem

FILE_NAME_SEPARATOR_UNIX = '/'
FILE_NAME_SEPARATOR_WIN = '\/'
fileNameSeparator = FILE_NAME_SEPARATOR_UNIX if platform.system() in ['Darwin', 'Linux']  else FILE_NAME_SEPARATOR_WIN
# print(fileNameSeparator) # TODO check on Win filesystem

GIT_LS_TREE_COMMAND = 'git ls-tree --full-tree -r HEAD'  # <mode> SP <type> SP <object> TAB <file>

gitCommandResultStream = ''
process = subprocess.Popen(GIT_LS_TREE_COMMAND, shell=True, stdout=subprocess.PIPE)
while process.poll() is None:
    gitCommandResultStream += process.stdout.readline()


checkPathNameResult = {}
pathNotExists = []
pathNotCaseMatched = []

for line in gitCommandResultStream.split('\n'):
    # print(line)
    vals = line.split('\t')
    if len(vals) == 2:
        file_path = vals[1]
        names = file_path.split(fileNameSeparator)  ## TODO check separator

        namesPath = ''
        for name in names:
            # generate full path
            parentNamePath = namesPath
            namesPath = namesPath + fileNameSeparator + name

            if namesPath not in checkPathNameResult.keys():

                testPath = BASE_DIR + namesPath

                result = {}
                # check path exist
                result['isExist'] = os.path.exists(testPath)

                if result['isExist']:
                    # check case sensitive
                    sneakParentPath = BASE_DIR + parentNamePath
                    for filenames in os.listdir(sneakParentPath):
                        for filename in filenames:
                            result['caseMatch'] = True
                            if name.lower() == filename.lower() and name != filename:
                                # filename not case match
                                result['caseMatch'] = False
                                pathNotCaseMatched.append(namesPath)
                            break
                else:
                    # path not exist record
                    pathNotExists.append(namesPath)

                checkPathNameResult[namesPath] = result

if len(pathNotExists) != 0 or len(pathNotCaseMatched) != 0:
    print('RESULT path not exists:', pathNotExists)
    print('RESULT path not case matched:', pathNotCaseMatched)
else:
    pass
