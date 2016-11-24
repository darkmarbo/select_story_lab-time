#include <iostream>
#include <string.h>
#include <stdio.h>
using namespace std;
const int N = 10001;
int dp[2][N];
int foo(char* src, int srcLen, char* des, int desLen)
{
    int i, j;
    for(j = 0; j <= desLen; ++j)
    {
        dp[0][j] = j;
    }
    int a, b;
    for(i = 1; i <= srcLen; ++i)
    {
        dp[i&1][0] = i;
        for(j = 1; j <= desLen; ++j)
        {
            if(src[i] == des[j])
            {
                dp[i&1][j] = dp[(i-1)&1][j-1];
            }
            else
            {
                a = dp[i&1][j-1] + 1;
                b = dp[(i-1)&1][j] + 1;
                dp[i&1][j] = a < b ? a : b;
            }
        }
    }
    return dp[srcLen&1][desLen];
}

int main(int argc, char** argv) {
    if(argc <3)
    {
        cout<<"usage: exe lab res\n";
        return 0;
    }
    int len1=strlen(argv[1]);
    int len2=strlen(argv[2]);
    int ret = 0;
    //char src[N]="abcd",des[N]="b55cd";
    int len=foo(argv[1],len1,argv[2],len2);
    float wer = float(len)/float(len1);
    ret=int(wer*1000);
    printf("len1:%dlen2:%dretlen:%dwerfloat:%fwerint:%d\n",len1,len2,len,wer,ret);
    return 0;
}

