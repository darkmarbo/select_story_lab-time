#!/bin/sh

if(($# < 2))
then
    echo "usage: $0 res_dir out_file"
    exit 0
fi
rm -rf  $2
ls -1 $1|while read line
do
    #02092_result.txt
    name=${line%_result.txt}
    count=`grep "^$name" $1/$line|wc -l`
    if((2 == $count))
    then
        grep "^$name" $1/$line |sed '1d' >> $2
    else
        echo "err line::::::$line"
    fi
    
done
sort -n  $2 > tmp.ttt
mv tmp.ttt $2
