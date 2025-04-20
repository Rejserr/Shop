class ScannerInterface:
    def __init__(self):
        self.callback = None
        
    def start_scanning(self, callback):
        self.callback = callback
        
    def stop_scanning(self):
        self.callback = None

class ZebraScanner(ScannerInterface):
    def start_scanning(self, callback):
        super().start_scanning(callback)
        # Zebra TC21 specific implementation
        
class GenericScanner(ScannerInterface):
    def start_scanning(self, callback):
        super().start_scanning(callback)
        # Generic USB/Bluetooth scanner implementation
