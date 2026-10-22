"""Windows job ownership: deadline termination includes evaluator descendants."""
import ctypes,os
from ctypes import wintypes

class Job:
    def __init__(self):
        assert os.name=='nt','This execution contract uses Windows job supervision'
        class IO(ctypes.Structure):
            _fields_=[(x,ctypes.c_uint64) for x in ['ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount']]
        class BASIC(ctypes.Structure):
            _fields_=[('PerProcessUserTimeLimit',ctypes.c_int64),('PerJobUserTimeLimit',ctypes.c_int64),('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',wintypes.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]
        class EXT(ctypes.Structure):
            _fields_=[('BasicLimitInformation',BASIC),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
        k=self.k=ctypes.WinDLL('kernel32',use_last_error=True)
        for name,args,result in [
            ('CreateJobObjectW',[ctypes.c_void_p,wintypes.LPCWSTR],wintypes.HANDLE),
            ('SetInformationJobObject',[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD],wintypes.BOOL),
            ('AssignProcessToJobObject',[wintypes.HANDLE,wintypes.HANDLE],wintypes.BOOL),
            ('TerminateJobObject',[wintypes.HANDLE,wintypes.UINT],wintypes.BOOL),
            ('CloseHandle',[wintypes.HANDLE],wintypes.BOOL)]:
            fn=getattr(k,name);fn.argtypes=args;fn.restype=result
        self.handle=k.CreateJobObjectW(None,None)
        info=EXT();info.BasicLimitInformation.LimitFlags=0x2000 # kill on close
        if not self.handle or not k.SetInformationJobObject(self.handle,9,ctypes.byref(info),ctypes.sizeof(info)):
            raise ctypes.WinError(ctypes.get_last_error())
    def assign(self,process):
        if not self.k.AssignProcessToJobObject(self.handle,wintypes.HANDLE(int(process._handle))):raise ctypes.WinError(ctypes.get_last_error())
    def terminate(self):
        if not self.k.TerminateJobObject(self.handle,124):raise ctypes.WinError(ctypes.get_last_error())
    def close(self):
        if self.handle:self.k.CloseHandle(self.handle);self.handle=None

