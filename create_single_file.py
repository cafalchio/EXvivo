from tqdm.auto import tqdm
import numpy as np
from glob import glob
import os
import gc
gc.enable()


def fill_zeros(size, good_channels, data_path, amp_names):
    '''This function adds zeros to the end of files that are smaller than the majority
    The problem with this solution is that the files can be smaller because some parts
    were missing in the middle. Here the assumption is that the file was missing the 
    last part
    '''
    for filename in amp_names:
        if filename not in good_channels:
            filesize = int(os.path.getsize(data_path+filename)/2)
            print(f'Filling zeros {filename}')
            with open(data_path+filename, 'ab+') as fb:
                zeros = np.zeros(size-filesize).astype('int16')
                fb.write(zeros)
    

def get_good_channels(data_path, amp_names):
    '''
    return the size of the file in int16 bytes and the list of channels with that size
    '''
    sizes = []
    for filename in amp_names:
        try:
            sizes.append(int(os.path.getsize(data_path+filename)/2))
        except:
            print(f'{filename} not exist, create zeros file')
            np.zeros(max(sizes),dtype=np.int16).tofile(data_path+filename)
                
    sizes = [int(os.path.getsize(data_path+filename)/2) for filename in amp_names]
    size = max(sizes)
    return size, [amp_names[i] for i, sz in enumerate(sizes) if sz==size]


def connect_files(data_path, amp_names, chunk_sz=256):
    '''Create a NxM he simplest file format is the raw_binary one. 
        Suppose you have N channels
        c0,c1,...,cN

        And if you assume that ci(t)
        is the value of channel ci

        at time t, then your datafile should be a raw file with values
        c0(0),c1(0),...,cN(0),c0(1),...,cN(1),...cN(T)

    This is simply the flatten version of your recordings matrix, with size N x T
    returns: bad channels
    '''

    out_data = data_path + ''.join(data_path.split('/')[-3:]) + '2.bin'
    size, good_channels = get_good_channels(data_path, amp_names)
    fill_zeros(size, good_channels, data_path, amp_names)

    if size/chunk_sz > int(size/chunk_sz):
        n = int(size/chunk_sz)+1
    else:
        n = int(size/chunk_sz)
        
    for i in tqdm(range(0, size, n)):
        chunk = np.array([np.memmap(data_path+filename, dtype='int16')[i:i+n] 
                          for filename in sorted(amp_names)]).T.flatten()
                          
        if i == 0:
            with open(out_data, 'wb') as fb:
                fb.write(chunk.astype('int16').tobytes())
        else:
            with open(out_data, 'ab+') as fb:
                fb.write(chunk.astype('int16').tobytes())
    print('Done!')

def main():
    # Create file names
    ampA_names = [f'amp-A-00{i}.dat' for i in range(0,10)] + [f'amp-A-0{i}.dat' for i in range(10,64)]
    ampB_names = [f'amp-B-00{i}.dat' for i in range(0,10)] + [f'amp-B-0{i}.dat' for i in range(10,64)]
    ampC_names = [f'amp-C-00{i}.dat' for i in range(0,10)] + [f'amp-C-0{i}.dat' for i in range(10,64)]
    ampD_names = [f'amp-D-00{i}.dat' for i in range(0,10)] + [f'amp-D-0{i}.dat' for i in range(10,64)]

    data_path = '/mnt/g/HUMAN/HUMAN_241/241_slice2/'
    connect_files(data_path, ampD_names)

if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()