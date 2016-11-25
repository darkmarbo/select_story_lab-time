#!/bin/sh

######
#if(($#<4))
#then
#    echo "usage: $0 dir_lab ***.txt  file_out ***.lab.list "
#    exit 0
#fi
#
### nohup ./run.sh AMidsummerNightsDream/lab_ren AMidsummerNightsDream/txt/AMidsummerNightsDream.txt  AMidsummerNightsDream_out  AMidsummerNightsDream.lab.list &
#
#dir_lab=$1
#txt=$2
#out=$3
#lab_list=$4
#
#
##python select_wav.py $out_file $lab_txt $lab_txt.sel
#python select_wav.py ${dir_lab} ${txt} ${out} ${lab_list}
##grep "find_ok:" ${out} > ${out}.find

##grep -v "wer_str=0.00" ${out}.find > ${out}.find.err


dir_in=Tobi
dir_out=Tobi_out
mkdir -p ${dir_out}

ls -1 ${dir_in} |while read name_story 
do
    path_story="${dir_in}/${name_story}"
    echo "${path_story}"

    path_lab="${path_story}/lab_ren"
    path_txt="${path_story}/txt"

    if [ ! -d ${path_lab} ];then
        echo "${path_story}/ not exist lab_ren"
        continue;
    fi
    if [ ! -d ${path_txt} ];then
        echo "${path_story}/ not exist txt"
        continue;
    fi

    name_txt="${name_story}.txt"
    path_txt="${path_txt}/${name_txt}"
    if [ ! -f ${path_txt} ];then
        echo "${path_txt}/ ***.txt not exist!"
        continue;
    fi

### 提取 lab文件list 
    lab_list=${name_story}.lab.list
    ls -1 ${path_lab} > ${lab_list}
    python select_wav.py ${path_lab} ${path_txt} ${dir_out}/${name_story}_out  ${lab_list}
    rm -rf ${lab_list}

done 
