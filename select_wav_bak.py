#-*- coding: utf-8 -*-
from __future__ import division
import os
import sys
import string
import commands


if len(sys.argv) < 4:
    print "usage %s dir_time txt_cont log.txt"%(sys.argv[0])
    print "usage %s lab的目录 大txt   输出log "%(sys.argv[0])
    sys.exit(0)


dir_time=sys.argv[1]
lab_file=open(sys.argv[2],'r')
log_file=open(sys.argv[3],'w')

#log_file.write("index\tlabel\twav\trecog\twer\n")

#### 记录识别 wav_name:识别结果文本 
dict_res={}
list_res=[];

### 将 list_res  按照时间先后排序 
def sort_list_wav(list_res):
    list_new = [];
    for wav in list_res:
        
        ii = 0;
        ii_find = -1;
        ### 找到比它大的那个 index  
        for wav_new in list_new:
            if compare_wav(wav,wav_new)<-1:
                ii_find = ii;
                break;
            ii += 1;

        if ii_find == -1:
            list_new.append(wav);
        else:
            list_new.insert(ii_find,wav);

    return list_new;

#### 小于 -1 表示小于       大于1表示大于 
def compare_wav(name1,name2):
    ### 01_Track_01+12.0544+12.9575
    list_name1 = name1.split("+");
    list_name2 = name2.split("+");
    if len(list_name1) != 3 or len(list_name2) != 3:
        print("input err!name1=%s\tname2=%s"%(name1,name2));
        return -1;
    track1 = list_name1[0]
    track2 = list_name2[0]
    st1 = string.atof(list_name1[1])
    st2 = string.atof(list_name2[1])
    end1 = string.atof(list_name1[2])
    end2 = string.atof(list_name2[2])

    if cmp(track1,track2)<0: 
        return -2;
    elif cmp(track1,track2)>0: 
        return 2;

    if st1<st2:
        return -3;
    elif st1>st2:
        return 3;

for line in res_file.readlines():

    line = line[:-1]
    #if len(line)==0:
    #    continue;

    ### wav_name 
    idx_dot = line.find(' ')
    idx_wav = line[0:idx_dot]

    ### 识别结果文本 
    res = line[idx_dot+1:].strip()
    res_wav_up = res.upper()

    if dict_res.has_key(idx_wav):
        continue;
    if cmp(res_wav_up,"<UNK>")==0:
        continue;

    dict_res[idx_wav] = res_wav_up
    list_res.append(idx_wav);
    #print "%s\t%s"%(idx_wav, res_wav_up)

### 将list_res 按照时间先后排序 
list_res = sort_list_wav(list_res);
for line in list_res:
    print("list_res:%s"%(line));

### 识别结果总行数 
M = len(dict_res.keys());
if M != len(list_res):
    print("map_len:%d != list_len:%d"%(M, len(list_res)));
    sys.exit(0);

dict_res['err'] ='err'

### 正确文本总行数 
N = 0;
for line in lab_file.readlines():
    line = line[:-1];
    if len(line)>0:
        N += 1;

#print("M_rec=%d\tN_lab=%d"%(M,N));
lab_file.close()

##### lab.txt
#### 为每一个正确的文本句子 找一个or多个连续wav 对应 
lab_file=open(sys.argv[2],'r')
### 第几个 lab 句子 
ii=0;
st_last_ok = -1;
for line in lab_file.readlines():
    line=line[:-1]
    ii += 1;

    lab_wav = line.strip()
    lab_wav_up = lab_wav.upper()
    ### 处理掉原始句子中包含的 "" 等 
    lab_wav_up = lab_wav_up.replace("\"","");


    #### 确定 从rec文件的 st end 范围 查找 
    st = ii;
    end = 0;
    end_tmp = 0;

    if ii<20:
        st=0;

    ### 上一个最靠谱的结果 index 
    if st<st_last_ok:
        st = st_last_ok;

    if M-(N-ii)>2*ii:
        end_tmp = 2*ii;
    else:
        end_tmp = M-(N-ii);

    if end_tmp-st > 20:
        end = end_tmp;
    else:
        end = st + 20;

    #### jj 介于 st和end之间时  才计算在内 
    idx_ok='err'
    wer_ok=1.0
    wer=1.0
    ### 找到的匹配项 下标 
    jj_find = -1;

    for jj in range(0,M):

        if jj<st-1 or jj>end:
            continue;
        k = list_res[jj];

        log_file.write("ii=%d\tst=%d\tend=%d\tkey=%s\tvalue=%s\tlab=%s\n"%(ii,st,end,k,dict_res[k],lab_wav_up))

        cmd="./wer \"%s\" \"%s\""%(lab_wav_up, dict_res[k])
        (ret,out) = commands.getstatusoutput(cmd)
        wer_str = out[out.find('werfloat:')+9:out.find('werint')]
        #log_file.write("cmd_wer:%s\twer_out=%s\twer_str=%s"%(cmd, out, wer_str))
        wer = string.atof(wer_str)
        #log_file.write("\twer_float=%.4f\n"%(wer))

        if wer < wer_ok:
            wer_ok = wer
            idx_ok = k
            jj_find = jj;

    ### 肯定准确的那个  
    if jj_find != -1 and wer_ok < 0.1:
        st_last_ok = jj_find;
        log_file.write("%s\t%.4f\t%s\t%s\n"%(idx_ok,wer_ok,lab_wav,dict_res[idx_ok]))
        log_file.flush()
        continue;

    ### 把jj_find 的上2句 下两句连起来 看看wer是否会降低 
    ### -2 -1 0 1 2 
    arr_wer = [0,0,1,0,0];
    rec_ok = dict_res[idx_ok]; ### 记录为最匹配的rec结果集合   
    rec_tmp = rec_ok;

    ### 左侧1个 
    if jj_find > 0:
        ### 加上左侧rec结果 
        rec_tmp = dict_res[list_res[jj_find-1]] + rec_ok;
        cmd="./wer \"%s\" \"%s\""%(lab_wav_up, rec_tmp)
        (ret,out) = commands.getstatusoutput(cmd)
        wer_str = out[out.find('werfloat:')+9:out.find('werint')]
        #log_file.write("cmd_wer:%s\twer_out=%s\twer_str=%s"%(cmd, out, wer_str))
        wer = string.atof(wer_str)

        ### 加上左1后的wer下降 
        if wer < wer_ok:
            ### 修改全局结果 已成定局  
            arr_wer[1]=1;
            rec_ok = dict_res[list_res[jj_find-1]] + rec_ok;
            wer_ok = wer;

            ### 尝试左侧2个
            if jj_find > 1:
                ### 加上左侧rec结果 
                rec_tmp = dict_res[list_res[jj_find-2]] + rec_ok;
                cmd="./wer \"%s\" \"%s\""%(lab_wav_up, rec_tmp)
                (ret,out) = commands.getstatusoutput(cmd)
                wer_str = out[out.find('werfloat:')+9:out.find('werint')]
                #log_file.write("cmd_wer:%s\twer_out=%s\twer_str=%s"%(cmd, out, wer_str))
                wer = string.atof(wer_str)

                ### 加上左2后的wer下降 
                if wer < wer_ok:
                    ### 修改全局结果 已成定局  
                    arr_wer[0]=1;
                    rec_ok = dict_res[list_res[jj_find-2]] + rec_ok;
                    wer_ok = wer;

    ### 右侧 1个 
    if jj_find+1<M:
        ### 加上右侧rec结果 
        rec_tmp = rec_ok + dict_res[list_res[jj_find+1]];
        cmd="./wer \"%s\" \"%s\""%(lab_wav_up, rec_tmp)
        (ret,out) = commands.getstatusoutput(cmd)
        wer_str = out[out.find('werfloat:')+9:out.find('werint')]
        #log_file.write("cmd_wer:%s\twer_out=%s\twer_str=%s"%(cmd, out, wer_str))
        wer = string.atof(wer_str)

        ### 加上右侧1个后的wer下降 
        if wer < wer_ok:
            ### 修改全局结果 已成定局  
            arr_wer[3]=1;
            rec_ok = rec_ok + dict_res[list_res[jj_find+1]] ;
            wer_ok = wer;

            ### 尝试右侧2个
            if jj_find +2 < M:
                ### 加上右侧rec结果 
                rec_tmp = rec_ok + dict_res[list_res[jj_find+2]];
                cmd="./wer \"%s\" \"%s\""%(lab_wav_up, rec_tmp)
                (ret,out) = commands.getstatusoutput(cmd)
                wer_str = out[out.find('werfloat:')+9:out.find('werint')]
                #log_file.write("cmd_wer:%s\twer_out=%s\twer_str=%s"%(cmd, out, wer_str))
                wer = string.atof(wer_str)

                ### 加上左2后的wer下降 
                if wer < wer_ok:
                    ### 修改全局结果 已成定局  
                    arr_wer[4]=1;
                    rec_ok = rec_ok + dict_res[list_res[jj_find+2]];
                    wer_ok = wer;
   
    ####   统计出最好的结果 
    track =  list_res[jj_find].split("+")[0];
    st_mix = list_res[jj_find].split("+")[1];
    end_mix = list_res[jj_find].split("+")[2];

    if arr_wer[0]==1:
        wav_name_2 = list_res[jj_find-2];
        track_2 = wav_name_2.split("+")[0]; 

        if cmp(track_2,track) != 0:
            print("ERROR:track2 != track0");
            continue;
        st_mix = wav_name_2.split("+")[1]; 
    elif arr_wer[1]==1:
        st_mix = list_res[jj_find-1].split("+")[1];

    if arr_wer[4]==1:
        wav_name_2 = list_res[jj_find+2];
        track_2 = wav_name_2.split("+")[0]; 

        if cmp(track_2,track) != 0:
            print("ERROR:track2 != track0");
            continue;
        end_mix = wav_name_2.split("+")[2]; 
    elif arr_wer[3]==1:
        end_mix = list_res[jj_find+1].split("+")[2];

    last_wav = "%s+%s+%s"%(track, st_mix, end_mix)

    #### 找到最靠谱的那个  
    if idx_ok != 'err':
        log_file.write("%s\t%.4f\t%s\t%s\n"%(last_wav, wer_ok, lab_wav, rec_ok))
        log_file.flush()

res_file.close()
lab_file.close()
log_file.close()
            

