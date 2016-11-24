#-*- coding: utf-8 -*-
from __future__ import division
import os
import sys
import string
import commands


if len(sys.argv) < 4:
    print "usage %s lab.txt res.txt log.txt"%(sys.argv[0])
    sys.exit(0)

count_all_sentence=0
count_ok_sentence=0
count_all_word=0
count_err_word=0

log_file=open(sys.argv[3],'w')
log_file.write("index\tlabel\twav\trecog\twer\n")

dict_lab={}
dict_lab['err']='err'
lab_file=open(sys.argv[1],'r')
for line in lab_file.readlines():
    if line[-1] == '\n':
        line=line[:-1]
    idx_dot=line.find('#')
    idx_wav=line[0:idx_dot]
    lab=line[idx_dot+1:].strip()
    lab_wav_up=lab.upper()
    dict_lab[idx_wav]=lab_wav_up
    #print "%s\t%s"%(idx_wav,lab)
    #print lab_wav_up

### res.txt
res_file=open(sys.argv[2],'r')
for line in res_file.readlines():
    if line[-1] == '\n':
        line=line[:-1]
    idx_dot=line.find('#')
    idx_wav=line[0:idx_dot]
    res_wav=line[idx_dot+1:].strip()
    res_wav_up=res_wav.upper()
    idx_ok='err'
    wer_ok=1.0
    wer=1.0
    if not dict_lab.has_key(idx_wav):
        print "%s not in dict_lab!"%(idx_wav)
        continue
    lab_wav=dict_lab[idx_wav]
    lab_len=len(lab_wav)
    #log_file.write("res_line k:%s  value:%s\n"%(k,dict_res[k]))
    cmd="./wer \"%s\" \"%s\""%(lab_wav,res_wav_up)
    (ret,out)=commands.getstatusoutput(cmd)
    #print out
    wer_str=out[out.find('werfloat:')+9:out.find('werint')]
    wer=string.atof(wer_str)
    print "lab:%s\tlen:%d\tres:%s\twer:%f\n"%(lab_wav,lab_len,res_wav_up,wer)



   #     if wer < wer_ok:
   #         wer_ok=wer
   #         idx_ok=k

   # if idx_ok != 'err':
   #     log_file.write("%s\t%s\t%s\t%s\t%f\n"%(idx_wav,lab_wav,idx_ok,dict_lab[idx_ok],wer_ok))
   #     log_file.flush()

lab_file.close()
res_file.close()
log_file.close()
            

