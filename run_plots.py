import os

files = [
        # r'C:\Users\cafa\Documents\CLUSTER\218\slice1A\HUMAN218human_151124_145847_A.bin',
        # r'C:\Users\cafa\Documents\CLUSTER\243\slice2\HUMAN_243_newslice2_new.bin',
        r'C:\Users\cafa\Documents\CLUSTER\243\slice3\HUMAN_243_newslice3_new.bin',
        r'C:\Users\cafa\Documents\CLUSTER\243\slice4\HUMAN_243_newslice3_new.bin',
        ]

for i, file in enumerate(files):
    print('===============================================================')
    print('Running spyking circus on')
    print(f'spyking-circus {file} -c 16 ')
    print('===============================================================')
    print(f'{i}/{len(files)}')
    os.system(f'spyking-circus {file} -c 16 ')
    # os.system(f'spyking-circus {file} -m converting -c 16 ')
    print('=============================================================\n\n')