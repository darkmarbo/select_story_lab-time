#!/bin/sh

#####
if(($#<4))
then
    echo "usage: $0 dir_lab ***.txt  file_out ***.lab.list "
    exit 0
fi

## nohup ./run.sh AMidsummerNightsDream/lab_ren AMidsummerNightsDream/txt/AMidsummerNightsDream.txt  AMidsummerNightsDream_out  AMidsummerNightsDream.lab.list &

dir_lab=$1
txt=$2
out=$3
lab_list=$4


#python select_wav.py $out_file $lab_txt $lab_txt.sel
python select_wav.py ${dir_lab} ${txt} ${out} ${lab_list}
#grep "find_ok:" ${out} > ${out}.find
#grep -v "wer_str=0.00" ${out}.find > ${out}.find.err


