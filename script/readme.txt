import ctypes
so = ctypes.CDLL("./libsplitwav.so")

nRet = so.splitWave(wavfile,segfile_file,spos,epos)
