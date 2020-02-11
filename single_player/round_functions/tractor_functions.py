class Tractor(object):
    def __init__(self, highest_card_value, length):
        self.high_card_value = highest_card_value
        self.length = length

    def __gt__(self, other):
        if self.high_card_value > other.high_card_value:
            return True
        return False

    def __cmp__(self, other):
        if self.high_card_value > other.high_card_value:
            return 1
        elif self.high_card_value == other.high_card_value:
            return 0
        else:
            return -1

    def get_highest_value(self):
        return self.high_card_value

    def get_tractor_length(self):
        return self.length

