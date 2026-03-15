class AssemblerError(Exception):
    """Raised for any assembly-time error in the SimpleRISC encoder."""

    def __init__(self, message, line_number=None):
        self.message = message
        self.line_number = line_number
        super().__init__(self._format())

    def _format(self):
        if self.line_number is not None:
            return f"Error on instruction line {self.line_number}: {self.message}"
        return f"Error: {self.message}"
