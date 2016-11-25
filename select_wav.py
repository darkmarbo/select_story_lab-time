#-*- coding: utf-8 -*-
from __future__ import division
import os
import sys
import string
import commands

WER_1 = 0.08
WER_2 = 0.1
TTP="turn the page"
DING="DING"


### 从lab目录中 读取每个文件中的时间信息和文本行
### 返回 list_key_sort, dict_time 
def read_dir_time(dir_name, file_list):

    list_key_sort = [];
    dict_time = {};

    fp_list = open(file_list);
    for file in fp_list:

        file = file[:-1]
        track = file.replace(".lab","");

        path_file = "%s/%s"%(dir_name, file)
        fp = open(path_file);
        for line in fp:
            line = line[:-1];

            vec_line = line.split("\t");
            if len(vec_line)<3:
                print("ERROR:lab line=%s\t format err!"%(line));
                continue;

            st = vec_line[0]
            end = vec_line[1]
            cont = vec_line[2]
            track_time = "%s+%s+%s"%(track, st, end);

            #fp_log.write("%s\t%s\t"%(st,end));
            #fp_log.write("%s\n"%(track_time));

            cont = cont.lower();
            cont = cont.replace("\"","");
            cont = cont.replace(",","");
            cont = cont.replace(".","");
            cont = cont.replace("!","");
            cont = cont.replace("?","");

            if cont == "#" or len(cont) == 0:
                continue;


            #### 08_Track_08+1.198168+3.143423  here
            if dict_time.has_key(track_time):
                print("ERROR:dict_time has key=%s "%(track_time));
                continue;

            list_key_sort.append(track_time);
            dict_time[track_time] = cont;


    dict_time['err'] = 'err';
    return (list_key_sort, dict_time);

def dict_sort_key(dt): 
    keys = dt.keys() 
    keys.sort() 
    return map(dt.get, keys) 

#### 将 list_res  按照时间先后排序 
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

def wer_get(lab, res):

    cmd="./wer \"%s\" \"%s\""%(lab, res)

    (ret,out) = commands.getstatusoutput(cmd)
    wer_str = out[out.find('werfloat:')+9:out.find('werint')]
    wer = string.atof(wer_str)

    return wer;

def fun_bak_line(line_bak, line):
    line_bak_new = line_bak;
    for ii in range(0,len(line_bak)-1):
        line_bak_new[ii] = line_bak[ii+1];
    line_bak_new[len(line_bak)-1] = line;
    return line_bak_new;

if __name__ == '__main__':

    if len(sys.argv) < 5:
        print "usage %s dir_time txt_cont log.txt file_lab_list "%(sys.argv[0])
        print "usage %s lab的目录 大txt   输出log lab列表"%(sys.argv[0])
        sys.exit(0)
    
    
    dir_time = sys.argv[1]
    fp_txt = open(sys.argv[2],'r')
    fp_out_ok = open(sys.argv[3],'w')
    file_lab_list = sys.argv[4];

    file_err="%s.err"%(sys.argv[3])
    file_log="%s.log"%(sys.argv[3])
    fp_log = open(file_log,"w");
    fp_err = open(file_err,"w");
    
    ### 读取lab-time 到dict_time中 
    #### track01+st+end content 
    list_key_sort,dict_time = read_dir_time(dir_time,file_lab_list);
    N = len(list_key_sort);

    fp_log.write("LOG:dict_time len_N=%d\n"%(N));
    for key in list_key_sort:
        fp_log.write("LOG:dict_time:%s\t%s\n"%(key, dict_time[key]));

#----------------------------------------------------------------------------------------

    ### 解决 txt 文本中的每一行 
    ii = 0;  ### 处理到大文本的第几行 
    ST_jj = 0; ### 每次从这个 index 开始查找 
    ST_jj_last = -1;  ### 上一个 wer=0.0000 的句子编号jj 
    line_bak=["","","","",""];
    for line in fp_txt:

        line = line[:-1]
        if len(line)==0:
            continue;
        
        ii += 1;
        ### 它和它的前4个 
        line_bak = fun_bak_line(line_bak, line);

        line_low = line.strip().lower();
        line_low = line_low.replace("\"","");
        line_low = line_low.replace(",","");
        line_low = line_low.replace(".","");
        line_low = line_low.replace("!","");
        line_low = line_low.replace("?","");

        #### 查找
        tk_tm_ok = 'err'
        wer_ok = 1.0
        cmd_ok = "err"
        jj_find = -1; ### 找到的匹配项 下标 
        wer_str="";

        MAX_JJ = ST_jj + 20;
        if MAX_JJ > N:
            MAX_JJ = N;

        #### 初始查找 
        fp_log.write("\n\nnum_txt=%d\tjj范围[%d\t%d]\t"%(ii,ST_jj,MAX_JJ));
        for jj in range(ST_jj, MAX_JJ):

            tk_tm = list_key_sort[jj];
            cont_res = dict_time[tk_tm];
            #fp_log.write("\n\n\njj=%d\ttrack_name=%s\tcont=%s\n"%(jj,tk_tm,cont_res));

            cmd="./wer \"%s\" \"%s\""%(line_low, cont_res)
            wer = wer_get(line_low, cont_res);
            fp_log.write("jj=%d\tcmd_wer:%s\twer_float=%.4f\n"%(jj, cmd, wer))

            if wer < wer_ok:
                wer_ok = wer
                tk_tm_ok = tk_tm
                jj_find = jj;
                cmd_ok = cmd;

                ### 结束查找 wer<WER_1
                if wer < 0.03:
                    ### 相差10句内找到了一个最匹配的
                    if (jj == ST_jj_last+1) or ((line.split())>6 and ST_jj+10>jj):
                        ST_jj = jj;
                    ST_jj_last = jj;
                    break;

        ###  单句  找到了 
        if wer_ok < WER_1:
            vec_tk = tk_tm_ok.split("+");
            tk_name_tmp = vec_tk[0]
            st_tmp = vec_tk[1]
            end_tmp = vec_tk[2]

            fp_out_ok.write("%s\t%s\t%s\t%s\n"%(tk_name_tmp, st_tmp, end_tmp, line))
            fp_out_ok.flush()
            continue;

        #################################################################################
        ### 1. 连接上一句  利用 jj_find 
        if jj_find > 0:
            tk_tm_1 = list_key_sort[jj_find-1];
            cont_res = dict_time[tk_tm_1] + " " + dict_time[tk_tm_ok];
            #fp_log.write("\n\n\njj=%d\ttrack_name=%s\tcont=%s\n"%(jj,tk_tm,cont_res));

            cmd="./wer \"%s\" \"%s\""%(line_low, cont_res)
            wer = wer_get(line_low, cont_res);
            fp_log.write("connect_1:%s\t%s\twer_float=%.4f\n"%(line_low,cont_res,wer))

            ### 得到拼接后的 wav名字和时间段 
            vec_tk_1 = tk_tm_1.split("+"); 
            vec_tk_ok = tk_tm_ok.split("+"); 
            if len(vec_tk_1) != 3 or len(vec_tk_ok) != 3:
                continue;
            track_conn = "%s+%s+%s"%(vec_tk_ok[0], vec_tk_1[1], vec_tk_ok[2]);

            ### 中间那个 # 的时间差 大不大 
            time_minus = string.atof(vec_tk_ok[1]) - string.atof(vec_tk_1[2]);
            #print("%.4f"%(time_minus));

            #### 2句 找到了 刚好拼接上 并且中间没有 叮
            if wer < WER_2 and time_minus < 0.020 :
                ### 找到了 完全可以拼接回去 
                wer_ok = wer
                vec_tk = track_conn.split("+");
                tk_name_tmp = vec_tk[0]
                st_tmp = vec_tk[1]
                end_tmp = vec_tk[2]
                fp_out_ok.write("%s\t%s\t%s\t%s\n"%(tk_name_tmp, st_tmp, end_tmp, line))
                fp_out_ok.flush()
                continue;
            elif wer < WER_2:
                ### 当前句 turn the page
                tk_tm_ttp = list_key_sort[jj_find];
                line_ttp = dict_time[tk_tm_ttp]
                wer_ttp = wer_get(TTP, line_ttp);
                if wer_ttp < 0.3:
                    #### 中间有叮  输出3句  上一句 叮  下一句  

                    ### 上一句 
                    tk_tm_1 = list_key_sort[jj_find-1];
                    vec_tk = tk_tm_1.split("+");
                    tk_name_tmp = vec_tk[0]
                    st_tmp = vec_tk[1]
                    end_tmp = vec_tk[2]
                    line_tmp = dict_time[tk_tm_1];  ### 上一句文本 

                    fp_out_ok.write("%s\t%s\t%s\t%s\n"%\
                                (tk_name_tmp, st_tmp, end_tmp, line_tmp))
                    fp_out_ok.flush()

                    ### 当前句  的时间信息  
                    tk_tm_ttp = list_key_sort[jj_find];
                    vec_tk = tk_tm_ttp.split("+");
                    st_2 = vec_tk[1]
                    end_2 = vec_tk[2]

                    ### DING 
                    fp_out_ok.write("%s\t%s\t%s\t%s\n"%\
                                (tk_name_tmp, end_tmp, st_2, DING))
                    fp_out_ok.flush()

                    ### 下一句  
                    fp_out_ok.write("%s\t%s\t%s\t%s\n"%\
                                (tk_name_tmp, st_2, end_2, line_ttp))
                    fp_out_ok.flush()

                    continue;

            if wer < wer_ok:
                wer_ok = wer
                fp_err.write("connect_left\t%s\t%s\twer_float=%.4f\n"%(line, cont_res,wer))
                fp_err.flush()
                continue;

        #### 2.连接下一句 
        if jj_find+1<N:
            tk_tm_1 = list_key_sort[jj_find+1];
            cont_res = dict_time[tk_tm_ok] + " " +dict_time[tk_tm_1];

            cmd="./wer \"%s\" \"%s\""%(line_low, cont_res)
            wer = wer_get(line_low, cont_res);
            fp_log.write("connect_2:%s\t%s\twer_float=%.4f\n"%(line_low,cont_res,wer))

            ### 得到拼接后的 wav名字和时间段 
            vec_tk_1 = tk_tm_1.split("+"); 
            vec_tk_ok = tk_tm_ok.split("+"); 
            if len(vec_tk_1) != 3 or len(vec_tk_ok) != 3:
                continue;
            track_conn = "%s+%s+%s"%(vec_tk_ok[0], vec_tk_ok[1], vec_tk_1[2]);

            time_minus = string.atof(vec_tk_1[1]) - string.atof(vec_tk_ok[2]);
            #print("%.4f"%(time_minus));

            if wer < WER_2 and time_minus < 0.020 :
                ### 找到了 完全可以拼接回去 
                wer_ok = wer
                vec_tk = track_conn.split("+");
                tk_name_tmp = vec_tk[0]
                st_tmp = vec_tk[1]
                end_tmp = vec_tk[2]
                fp_out_ok.write("%s\t%s\t%s\t%s\n"%(tk_name_tmp, st_tmp, end_tmp, line))
                fp_out_ok.flush()
                continue;
            elif wer < WER_2:
                ### 下一句是  turn the page
                tk_tm_ttp = list_key_sort[jj_find+1];
                line_ttp = dict_time[tk_tm_ttp]
                wer_ttp = wer_get(TTP, line_ttp);
                if wer_ttp < 0.3:
                    #### 中间有叮  输出3句  上一句 叮  下一句  
                    print("test....");

                    ### 当前句  
                    tk_tm_1 = list_key_sort[jj_find];
                    vec_tk = tk_tm_1.split("+");
                    tk_name_tmp = vec_tk[0]
                    st_tmp = vec_tk[1]
                    end_tmp = vec_tk[2]
                    line_tmp = line_bak[3];   

                    fp_out_ok.write("%s\t%s\t%s\t%s\n"%\
                                (tk_name_tmp, st_tmp, end_tmp, line_tmp))
                    fp_out_ok.flush()

                    ### 当前句  的时间信息  
                    vec_tk = tk_tm_ttp.split("+");
                    st_2 = vec_tk[1]
                    end_2 = vec_tk[2]

                    ### DING 
                    fp_out_ok.write("%s\t%s\t%s\t%s\n"%\
                                (tk_name_tmp, end_tmp, st_2, DING))
                    fp_out_ok.flush()

                    ### 下一句  
                    fp_out_ok.write("%s\t%s\t%s\t%s\n"%\
                                (tk_name_tmp, st_2, end_2, line_ttp))
                    fp_out_ok.flush()

                    continue;

            if wer < wer_ok:
                wer_ok = wer
                #fp_err.write("%s\t%s\t%s\n"%(tk_tm_ok, line, dict_time[tk_tm_ok] ))
                fp_err.write("connect_right\t%s\t%s\twer_float=%.4f\n"%(line, cont_res, wer))
                fp_err.flush()
                continue;

        #### 还是没有  
        fp_err.write("%s\t%s\t%s\n"%(tk_tm_ok, line, dict_time[tk_tm_ok] ))
        fp_err.flush()
            
#----------------------------------------------------------------------------------------
    

    fp_log.write("process txt line len=%d\n"%(ii));
    fp_txt.close()
    fp_out_ok.close()
    fp_err.close()




