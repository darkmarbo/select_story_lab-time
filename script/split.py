import ctypes
import sys
import string
so = ctypes.CDLL("./libsplitwav.so")

#nRet = so.splitWave(wavfile,segfile_file,spos,epos)
print "python_splitwave............"
st=int(string.atof(sys.argv[3]))*1000
ed=int(string.atof(sys.argv[4]))*1000
print "st:%f\ted:%f"%(st,ed)
nRet = so.splitWave(sys.argv[1],sys.argv[2],st,ed)
print nRet
