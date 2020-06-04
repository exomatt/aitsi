class Reference:

    def __init__(self, element: str, reference: str):
        self.reference = str(reference)
        self.element = str(element)

    def __repr__(self):
        return f'({self.element.__repr__()}({self.reference.__repr__()}))'

    def reverse(self):
        return Reference(self.reference, self.element)
