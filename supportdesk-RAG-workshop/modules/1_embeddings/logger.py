class Logger:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self.logs = []
    
    def log(self, message):
        self.logs.append(message)
    
    def save_logs(self, filename):
        with open(filename, 'a') as f:
            for message in self.logs:
                f.write(f"{message}\n")