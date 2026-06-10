class CommState:
    def __init__(self):

        self.busy = False
        self.done = False

        self.color = "blue"

        self.client_ready = False

        self.com_get_command = False

        self.com_get_hex_data = False
        self.com_got_hex_word = False

        self.hex_buffer = ""
        self.last_hex_word = ""

        self.prompt_received = 0

        self.load_srec = False

        self.irsp = 0

        self.no_report = False

        self.broken = False
        
        self.current_line = ""
        
        self.console_buffer = []
        self.last_response = ""
        
        self.color = "blue"     
         
        self.done = False       
        self.broken = False      
        
        self.cpu_exception_result = None
        self.fpu_exception_result = None
