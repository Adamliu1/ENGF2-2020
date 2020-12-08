class UnknownInstructionException(Exception):
    pass


class BlockLimitException(Exception):
    #print(board.score)
    pass


class NoBlockException(Exception):
    def __init__(self):
        super().__init__("This board has no block to manipulate.")
