#!/usr/bin/env python3

from time import perf_counter
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor, wait
from functools import partial
import argparse
import sys
import subprocess

def pygrep(file=None,verbose=False,word=None):
# Given file path(s) and search word, open each file and print lines containing search word
# if verbose = True, function will print filename:line number: line contents
# if file cannot be opened or the object is a directory, skip error.
    try:
        with open(file,'r') as f:
            text=f.readlines()
            for no,line in enumerate(text,start=1):
                if word in line and verbose:
                    print('{}:{}:{}'.format(file,no,line.strip()).strip())
    except:
        return

def time_it(func):
# decorator function to time the multigrep function in this module, returns elapsed time in milliseconds
# will print time after function is completed
    def wrapper(*args,**kwargs):
        start=perf_counter()
        func(*args,**kwargs)
        end=perf_counter()
        print('{:.5f} milliseconds'.format((end-start)*1000))
    return wrapper

@time_it
def multigrep(verbose=False,mode=None,word=None,files=[]):
    #launches pygrep function using multithreading, multiprocess, or single process modes
    #choose Exector type based on mode selection, either thread or process.
    #launches pool with map function, uses partial function to use same word and verbose values for each run type
    #only the multiple filenames are mapped to the executor.
    #executor.shutdown function is called to ensure all work is completed before reporting elapsed time
    #if mode is not given, the single thread pygrep is run for each file
    executors={'thread':ThreadPoolExecutor,'process': ProcessPoolExecutor}
    if mode in executors.keys():
        with executors[mode](max_workers=20) as executor:
            print(executor.__class__.__name__)
            result=executor.map(partial(pygrep,word=word,verbose=verbose),files)

    else:
        print('no parallelism')
        for file in files:
            pygrep(file=file,word=word,verbose=verbose)

def get_args():
    #parser used if program is run from command line
    #can choose which mode to run for concurrency or run all
    #optional flag for turning on verbose output from the pygrep function
    #positional arguments are word and file(s)
    parser = argparse.ArgumentParser(description='multigrep with python.')

    parser.add_argument('--mode','-m',help='select type',choices=['nonparallel','process','thread','all'],default='all')
    parser.add_argument('--verbose', '-v',help='display output',action='store_true')

    parser.add_argument('word',help='enter search word')
    parser.add_argument('files', metavar='filename',  nargs='+',
                        help='a file name path to search')
    args = parser.parse_args()
    return vars(args)


if __name__ == '__main__':
    #runs either commandline execution or internal IDE run
    modes = ['process', 'thread', None]

    #if sys argument were entered, run get_args function
    args=get_args()

    if args['mode']=='all':
        #run multigrep three times, one for each concurrency mode
        for mode in modes:
            args['mode']=mode
            multigrep(**args)
    else:
        # run either thread, process, or single thread based on mode entered
        multigrep(**args)

