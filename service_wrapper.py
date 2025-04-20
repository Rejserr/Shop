import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from waitress import serve
from run import app

class FTShopsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FTShopsService"
    _svc_display_name_ = "FT Shops Application Service"
    _svc_description_ = "Flask application service for FT Shops"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_alive = False

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    def main(self):
        try:
            app.config['SERVER_NAME'] = 'ftshops.fero-term.local:8000'
            serve(app, host='0.0.0.0', port=8000, url_scheme='http', _quiet=True)
        except Exception as e:
            servicemanager.LogErrorMsg(str(e))
            self.SvcStop()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(FTShopsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(FTShopsService)
        win32serviceutil.HandleCommandLine(FTShopsService)