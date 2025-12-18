class Console:
    @staticmethod
    def info(message: str):
        print(f"INFO: {message}")
    
    @staticmethod
    def error(message: str):
        print(f"ERROR: {message}")
    
    @staticmethod
    def warning(message: str):
        print(f"WARNING: {message}")
