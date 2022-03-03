import numpy as np
from glob import glob
from tqdm.auto import tqdm
import os, sys
import gc
import readline
gc.enable

### Still giving error at header ### - Tested on spike interface
########################################
# Path completer

def list_folder(path):
    """
    Lists folder contents
    """
    if path.startswith(os.path.sep):
        # absolute path
        basedir = os.path.dirname(path)
        contents = os.listdir(basedir)
        # add back the parent
        contents = [os.path.join(basedir, d) for d in contents]
    else:
        # relative path
        contents = os.listdir(os.getcwd())
    return contents


def completer(text, state):
    """
    Our custom completer function
    """
    options = [x for x in list_folder(text) if x.startswith(text)]
    return options[state]

readline.set_completer(completer)

if sys.platform == 'darwin':
    # Apple uses libedit.
    readline.parse_and_bind("bind -e")
    readline.parse_and_bind("bind '\t' rl_complete")
else:
    # Some tweaks for linux
    readline.parse_and_bind('tab: complete')
    readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>?')

###################################################################################
### Autocompleter END


ampA_names = [f'amp-A-00{i}.dat' for i in range(0,10)] + [f'amp-A-0{i}.dat' for i in range(10,64)]
ampB_names = [f'amp-B-00{i}.dat' for i in range(0,10)] + [f'amp-B-0{i}.dat' for i in range(10,64)]
ampC_names = [f'amp-C-00{i}.dat' for i in range(0,10)] + [f'amp-C-0{i}.dat' for i in range(10,64)]
ampD_names = [f'amp-D-00{i}.dat' for i in range(0,10)] + [f'amp-D-0{i}.dat' for i in range(10,64)]
AMPS = [ampA_names, ampB_names, ampC_names, ampD_names]
LOG = []

def create_dummy(size):
    return np.zeros(size).astype('int16')

def convert_mda(files, mda_file):
    over = ''
    if os.path.exists(mda_file):
        while over != 'y':
            over = input('\nFile already exists, do you want to overwrite?(y,n)')
            if over == 'n':
                return None
            elif over == 'y':
                continue

    dummyappend, dummyrec = None, None
    file_size = os.path.getsize(files[0])
    b1 = -4
    b2 = 2
    b3 = len(files)
    b4 = [os.path.getsize(files[0]) for _ in range(len(files))]
    bts = [b1, b2, b3] + b4
    header = np.array(bts).astype('int32')

    with open(mda_file, 'wb') as fb:
        fb.write(header.tobytes())

    for filename in tqdm(files):
        try:
            if os.path.getsize(filename) != file_size:
                if os.path.getsize(filename) - file_size < 0: #fill with 0
                    dummyappend = create_dummy(os.path.getsize(filename) - file_size)
                else:
                    raise ValueError(f'Filename with different size:\n{filename}')
        except:
            dummyrec = create_dummy()

        if not dummyappend and not dummyrec:
            temp = np.fromfile(filename, dtype=np.int16)*.195
            LOG.append(filename.split('/')[-1])

        elif dummyrec:
            temp = dummyrec

        else:
            temp = np.concatenate(np.fromfile(filename, dtype=np.int16)*.195, dummyappend)
            temp.astype('int16')
        with open(mda_file, 'ab+') as fb:
            fb.write(temp.tobytes())
        del temp
        gc.collect()


def main():
    data_path = input('Enter the recording path: ') + '/'
    amps_names = ['A', 'B', 'C', 'D']
    for i, fileAmps in enumerate(AMPS):
        try:
            files = [data_path+amp_name for amp_name in fileAmps] 
            print(len(files))
            print('\n#############################################\n')
            print(f'Converting amp-{amps_names[i]} files 0-32')
            convert_mda(files[0:32], data_path+f'amp{amps_names[i]}_0_32.mda')
            print('\nConverting amp-A files 32-64')
            convert_mda(files[32:], data_path+f'amp{amps_names[i]}_32_63.mda')#
        except:
            continue


    print('Done!')
    if len(LOG) > 0:
        print('\n#############################################')
        print('List of error channels:')
        print(LOG)

if __name__ == "__main__":
    main()