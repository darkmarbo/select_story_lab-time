#include "splitwav.h"

int readWavHeader(char *wavfile, _FILL_STRUCT *WaveHeader)
{
    int  ret;
	int nsize = 0;
    char *pt = NULL;
	FILE *fp = NULL;
	
	fp = fopen(wavfile,"r");
    if(fp == NULL){
        return -1;
    }

	_RIFF_HEADER riff_header;
	pt = (char *)&riff_header;
	ret = fread(pt,sizeof(char),sizeof(_RIFF_HEADER),fp);
	nsize += ret;
	WaveHeader->riff_header = riff_header;
	
	_FMT_BLOCK fmt_block;
	pt = (char *)&fmt_block;
	ret = fread(pt,sizeof(char),sizeof(_FMT_BLOCK),fp);
	nsize += ret;
	WaveHeader->fmt_block = fmt_block;
	
	//attach information
	if(WaveHeader->fmt_block.FmtSize == 18){
		ret = fread(pt,sizeof(char),2,fp);
		nsize += ret;
	}
	_FACT_BLOCK fact_block;
	pt = (char *)&fact_block;
	ret = fread(pt,sizeof(char),sizeof(_FACT_BLOCK),fp);
	WaveHeader->fact_block = fact_block;
	
	char sTmp[10];
	memcpy(sTmp,WaveHeader->fact_block.FactID,4);
	if(strcmp(sTmp,"fact") == 0){
		nsize += ret;
		_DATA_BLOCK data_block;
		pt = (char *)&data_block;
		ret = fread(pt,sizeof(char),sizeof(_DATA_BLOCK),fp);
		nsize += ret;
		WaveHeader->data_block = data_block;
    }
	else{                          
		memcpy(WaveHeader->data_block.DataID , WaveHeader->fact_block.FactID,4);
        WaveHeader->data_block.DataSize = WaveHeader->fact_block.FactSize;
		nsize += sizeof(_DATA_BLOCK);
    }

	pt = NULL;
	fclose(fp); 
	fp = NULL;
    return nsize;
}

int writeWavData(char *wavfile, _FILL_STRUCT *WaveHeader,char *data,long len)
{
	int nsize = 0;
	int ns = 0;
	FILE *fp = NULL;
	if ((fp = fopen(wavfile, "w")) == NULL)   
        return -1;

	//write riff_header
    WaveHeader->riff_header.RiffSize = len + sizeof(WaveHeader) - 8;
	ns = sizeof(_RIFF_HEADER);
	fwrite(&WaveHeader->riff_header,ns,1,fp);
	nsize += ns;
	
	//write fmt_block
	ns = sizeof(_FMT_BLOCK);
	fwrite(&WaveHeader->fmt_block,ns,1,fp);
	nsize += ns;
	if(WaveHeader->fmt_block.FmtSize == 18){
		fwrite("00",2,1,fp);
		nsize += 2;
		WaveHeader->riff_header.RiffSize += 2;
	}
	
	//write fact_block
	char sTmp[10];
	memcpy(sTmp,WaveHeader->fact_block.FactID,4);
	if(strcmp(sTmp,"fact") == 0){
		ns = sizeof(_FACT_BLOCK);
		fwrite(&WaveHeader->fact_block,ns,1,fp);
		nsize += ns;
    }

	//write data_block
	WaveHeader->data_block.DataSize = len;
	ns = sizeof(_DATA_BLOCK);
	fwrite(&WaveHeader->data_block,ns,1,fp);
	nsize += ns;
	
	fwrite(data, 1, len, fp);
	fseek(fp,0,SEEK_SET);
	fclose(fp); 
	fp = NULL;
	return nsize;
}

int splitWave(char *wavfile,char *dstfile,long spos,long epos)
{
	_FILL_STRUCT WaveHeader;
	int sRet,eRet;
	FILE *fp = NULL;
	
    sRet = readWavHeader(wavfile,&WaveHeader);
	if(sRet == -1)
		return 1001;
	
	long slen = spos * WaveHeader.fmt_block.AvgBytesPerSec/1000;
	long elen = epos * WaveHeader.fmt_block.AvgBytesPerSec/1000;
	long plen = elen - slen;
	
    char *data = (char*)malloc(sizeof(char)*(plen+1));	
	fp = fopen(wavfile,"r");
    if(fp == NULL){
        return -1;
    }
	fseek(fp,slen+sRet,SEEK_SET);
	fread(data, 1, plen, fp);
	eRet = writeWavData(dstfile,&WaveHeader,data,plen);
    if(sRet == -1)
		return 1002;
	
	free(data); 
	data = NULL;
    fclose(fp); 
	fp = NULL;
	return 0;
}

long getWavLength(char *wavfile)
{
	_FILL_STRUCT WaveHeader;
	int Ret;
	
    Ret = readWavHeader(wavfile,&WaveHeader);
	if(Ret == -1)
		return 0;
    return (long)((double)WaveHeader.data_block.DataSize / WaveHeader.fmt_block.AvgBytesPerSec * 1000);		
}

long getSampleRate(char *wavfile)
{
	_FILL_STRUCT WaveHeader;
	int Ret;
	
    Ret = readWavHeader(wavfile,&WaveHeader);
	if(Ret == -1)
		return 0;
    return WaveHeader.fmt_block.SamplesPerSec;
}





