#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef int DWORD;
typedef unsigned short WORD;
typedef struct _RIFF_HEADER
{
    char     RiffID[4];  //'R','I','F','F'
    DWORD    RiffSize;
    char     RiffFormat[4]; //'W','A','V','E'
}_RIFF_HEADER;

typedef struct _FMT_BLOCK
{
    char      FmtID[4]; //'f','m','t'
    DWORD     FmtSize;
    WORD      FormatTag;
    WORD      Channels;
    DWORD     SamplesPerSec;
    DWORD     AvgBytesPerSec;
    WORD      BlockAlign;
    WORD      BitsPerSample;
}_FMT_BLOCK;

typedef struct _FACT_BLOCK
{
    char      FactID[4]; //'f','a','c','t'
	DWORD     FactSize;
    DWORD     FactData;
}_FACT_BLOCK;

typedef struct _DATA_BLOCK
{
	char      DataID[4]; // 'd','a','t','a'
	DWORD     DataSize;
}_DATA_BLOCK;

 
typedef struct _FILL_STRUCT
{
    _RIFF_HEADER   riff_header;
    _FMT_BLOCK     fmt_block;
    _FACT_BLOCK    fact_block;
    _DATA_BLOCK    data_block;
}_FILL_STRUCT;

extern int  readWavHeader(char *wavfile, _FILL_STRUCT *WaveHeader);
extern int  writeWavData(char *wavfile, _FILL_STRUCT *WaveHeader,char *data,long len);
extern int  splitWave(char *wavfile,char *dstfile,long spos,long epos);
extern long getWavLength(char *wavfile);
extern long getSampleRate(char *wavfile);




 