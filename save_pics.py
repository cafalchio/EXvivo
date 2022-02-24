# Imports
import glob, os
from tqdm import tqdm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.fftpack import fft
from scipy.signal import welch

class Plot:
    def __init__(self, data, treatments, sf, title):
        self.data = data
        self.treatments = treatments
        self.sf = sf
        self.title = title

    def plot_nice(self):
        '''Adapted from Raphael Vallat blog
        '''
        colors = {
                'normal':'green',
                'modified':'red',
                'perapanel':'blue',
                'RO': 'yellow',
                'NVP': 'brown',
                '0Mg': 'purple',
                'Levetiracetam': 'orange',
                '4-AP': 'olive'
            }
        sns.set(font_scale=1.2)
        # Define sampling frequency and time vector
        time = np.arange(self.data.size) / self.sf
        # return time
        # Plot the signal
        ax = plt.figure(figsize=(20, 4))
        ax = plt.plot(time, self.data, lw=1.5, color='k')
        self.treatments[0] = [x*self.sf*60 for x in self.treatments[0]]
        self.treatments[0], self.treatments[1] = zip(*sorted(zip(self.treatments[0], self.treatments[1])))
        self.treatments[0], self.treatments[1] = list(self.treatments[0]), list(self.treatments[1])
        self.treatments[0].append(time.size-1)
        for i in range(len(self.treatments[1])):    
            ax = plt.axvspan(time[self.treatments[0][i]], time[self.treatments[0][i+1]], 
                            label=self.treatments[1][i], color=colors[self.treatments[1][i]], 
                            alpha=0.1)
        ax = plt.xlabel('Time (seconds)')
        ax = plt.ylabel('uV')
        ax = plt.title(self.title)
        ax = plt.xlim([time.min(), time.max()])
        ax = plt.legend(loc='upper right')
        plt.savefig(f'{self.title}_full.jpg', bbox_inches='tight')
        sns.despine()
        plt.close()    

    def calculteFFT(self):
        # Calculate FFT for the signal in windows of 1 minute
        # ffts = calculate_fft(channel_data, sf, window=1)
        # ffts.mean(axis=0)
        freqs, res_fft = welch(self.data, self.sf, window='hann', nperseg=8192, \
                        nfft = 8192, scaling = 'density', average='mean')
        sns.set(font_scale=1.2, style='white')
        idx_delta = np.logical_and(freqs >= 20, freqs <= 80)
        plt.figure(figsize=(4,4))
        plt.plot(freqs, res_fft)
        plt.xlim(2,100)
        # plt.ylim(0,0.02)
        plt.yticks(fontsize=8)
        plt.xticks(fontsize=8)
        idx = (freqs >=20.) & (freqs<=80)
        x = freqs[idx]
        y = res_fft[idx]
        plt.fill_between(freqs, res_fft, where=idx_delta, color='green', alpha=.4, label = 
                        f'gamma (20-80Hz)\npeak: {x[np.where(y == y.max())][0]:.1f}Hz\nArea: {np.trapz(x=x, y=y):.1f}')
        plt.xlabel('Frequency (Hz)', fontsize=9)
        plt.ylabel(r'$\frac{\mu V^2}{Hz}$')
        # plt.legend()
        plt.title(f'{self.title}', fontsize=9)
        plt.savefig(f'{self.title}_FFT.jpg', bbox_inches='tight')
        plt.close()
    

def input_treatment_times(df, slice):
    '''read_times for normal, modified and prepanel

    Input: 
        (df):dataframe with times and treatment
        (str):string of slice name
    Returns:
        list of treatment times
        list of treatment names 
    '''
    all_treats = ['normal', 'modified', 'change_position', 'RO', 'NVP', '0Mg', 'Levetiracetam', 'perapanel', '4-AP']
    clean_t = df.loc[df.slice == slice].dropna(axis=1)
    clean_t = clean_t[[x for x in clean_t.columns if x in all_treats]]
    treats_list = list(clean_t.columns)
    t_times_list = [i  if type(i)==str else str(i) for col in clean_t.columns for i in clean_t[col]]
    t_times_list = [x.split() for x in t_times_list]
    treats_list = [len(x)*[treat] for x, treat in zip(t_times_list, treats_list) ]
    times = sum(t_times_list, [])
    times = [int(float(i)) for i in times]
    return [times, sum(treats_list, [])]

def calculate_fft(x, sf,  window=1):
    '''Calculates the LFP of the signal in windows n minutes'''
    win = window * sf * 60
    g = int(len(x)/win)
    fftx = []
    for i in range(g):
        start = i*win
        end = i*win+win
        # print(len(data[start:end])/2500)
        fftx.append(fft(x[start:end], n=2048*4))
        break
    return np.array(fftx)

def find_eeg_files(path_to_data):
    files = sorted(glob.glob(path_to_data+'/amp-*1000.dat'))
    return files

def read_channel(channel_file):
    '''Function that reads a single LFP channel'''
    data_ch = np.fromfile(channel_file, dtype=np.int16)*.195
    return data_ch

##################################################################################
## RUN ##

def main():
    humans_to_plot =[
                # 'G:\\HUMAN\HUMAN 212\slice1_151002_185204\\downsampleLFP', Done!
                # 'G:\\HUMAN\HUMAN 213\\slice1_151008_165239\\downsampleLFP', Done
                # 'G:\\HUMAN\HUMAN 214\slice2_151015_165854\\downsampleLFP', Done!
                # 'G:\\HUMAN\HUMAN 214\slice1_151015_130152\\downsampleLFP', Done!
                # 'G:\\HUMAN\HUMAN 215\slice1_151020_133348\\downsampleLFP', Done!
                # 'G:\\HUMAN\HUMAN 215\slice2_151020_185053\\downsampleLFP',  Done!
                # 'G:\\HUMAN\HUMAN 216\session1_151106_154501\\downsampleLFP', Done!
                # # 'G:\\HUMAN\HUMAN 217\human_151110_122702\\downsampleLFP', Not in the list
                # 'G:\\HUMAN\HUMAN 218\human_151124_145847\\downsampleLFP', Done!
                # 'G:\\HUMAN\HUMAN 218\human_151124_172920\\downsampleLFP', Done!
                # 'G:\\HUMAN\HUMAN 218\human_151124_200111\\downsampleLFP', Done!
                # 'G:\\HUMAN\HUMAN 218\human_151124_124406\\downsampleLFP', Not in list
                # 'G:\\HUMAN\HUMAN 219\human_151126_145153\\downsampleLFP', Done!
                # 'G:\\HUMAN\HUMAN 220\human_151202_174443_n\\downsampleLFP', Not in Files
                # 'G:\\HUMAN\HUMAN 227\HUMAN227_160301_160429_n\\downsampleLFP',
                ]
    paths = r'G:\HUMAN\HUMAN 218\human_151124_145847\downsampleLFP' 
    df = pd.read_csv(r'g:/HUMAN/treatment_times.csv')
    sf = 1000
    print(f'{paths}')
    slice_name = paths.split('\\')[-2]
    rat = paths.split('\\')[-3].split()[-1]
    data_path = "\\".join(paths.split('\\'))
    save_path = "\\".join(paths.split('\\')[:-2])
    out_path = '\\' + 'figs_' + slice_name
    if not os.path.exists(save_path + out_path):
        os.makedirs(save_path + out_path)
    for ch, channel_file in enumerate(tqdm(find_eeg_files(data_path))):
        # if ch < 32:
        #     continue
        treatments = input_treatment_times(df, slice_name)
        data = read_channel(channel_file)
        title = f"{save_path+out_path}\\{rat}_{slice_name}_ch{ch}"
        plots = Plot(data, treatments, sf, title)
        plots.plot_nice()
        # plots.calculteFFT()



if __name__ == '__main__':
    # execute only if run as the entry point into the program
    log = main()

