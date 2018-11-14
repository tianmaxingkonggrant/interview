# -*- coding=utf-8 -*-


"""
Description

1) You decided to give up on earth after the latest financial collapse left 99.99% 
    of the earth's population with 0.01% of the wealth. Luckily, with the scant 
    sum of money that is left in your account, you are able to afford to rent a 
    spaceship, leave earth, and fly all over the galaxy to sell common metals and 
    dirt (which apparently is worth a lot).

2) Buying and selling over the galaxy requires you to convert numbers and units, 
    and you decided to write a program to help you. The numbers used for 
    intergalactic transactions follows similar convention to the roman numerals 
　　 and you have painstakingly collected the appropriate translation between them.

3) Numbers are formed by combining symbols together and adding the values. 
    For example, MMVI is 1000 + 1000 + 5 + 1 = 2006. Generally, symbols are 
    placed in order of value, starting with the largest values. When smaller 
    values precede larger values, the smaller values are subtracted 
    from the larger values, and the result is added to the total. 
　　 For example MCMXLIV = 1000 + (1000 − 100) + (50 − 10) + (5 − 1) = 1944.

4)
    1, The symbols "I", "X", "C", and "M" can be repeated three times in succession, but no more. 
          (They may appear four times if the third and fourth are separated by a smaller value, such as XXXIX.) 
    2, "D", "L", and "V" can never be repeated. "I" can be subtracted from "V" and "X" only. 
    3, "X" can be subtracted from "L" and "C" only. 
    4, "C" can be subtracted from "D" and "M" only. 
    5, "V", "L", and "D" can never be subtracted. 
    6, Only one small-value symbol may be subtracted from any large-value symbol. 
    7, A number written in Arabic numerals can be broken into digits. 
          For example, 1903 is composed of 1, 9, 0, and 3. To write the Roman numeral, 
          each of the non-zero digits should be treated separately. 
          In the above example, 1,000 = M, 900 = CM, and 3 = III. Therefore, 1903 = MCMIII.

5) Input to your program consists of lines of text detailing your notes on the conversion 
    between intergalactic units and roman numerals.

6) You are expected to handle invalid queries appropriately.

INPUT:
glob is I
prok is V
pish is X
tegj is L
glob glob Silver is 34 Credits
glob prok Gold is 57800 Credits            
pish pish Iron is 3910 Credits
how much is pish tegj glob glob ?
how many Credits is glob prok Silver ?
how many Credits is glob prok Gold ?
how many Credits is glob prok Iron ?


OUTPUT
pish tegj glob glob is 42
glob prok Silver is 68 Credits
glob prok Gold is 57800 Credits
glob prok Iron is 782 Credits

"""

import os
import sys
import time
import copy
import logging
import string
import argparse
import hashlib

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--input_file", type=str, default="input.txt",
                    help="file that you use to detail your notes on the conversion "
                         "between intergalactic units and roman numerals")
args = parser.parse_args()

ROMEN_ALAB = {'C': 100, 'CD': 400, 'CM': 900, 'D': 500, 'I': 1, 'IV': 4,
              'IX': 9, 'L': 50, 'M': 1000, 'V': 5, 'X': 10, 'XC': 90, 'XL': 40}
REPEATED_SYMBOLS = ["I", "X", "C", "M"]
NO_REPEATED_SYMBOLS = ["D", "L", "V"]


class TextParseEngine(object):
    """
    parse each line of text
    """
    PARSE_UNIT = "parse_unit"
    PARSE_SYMBOL = "parse_symbol"
    PARSE_ISSUE = "parse_issue"

    def __init__(self, parse_line, parse_line_number, parsed_symbols, parsed_units):
        self.parsed_symbols = parsed_symbols
        self.parsed_units = parsed_units
        self.parse_line = parse_line
        self.parse_line_number = parse_line_number
        self.line_contents = []
        self.parse_type = None
        self.symbols_roman = {}
        if self.parsed_symbols:
            self.symbols_roman = {v: k for k, v in self.parsed_symbols.items()}

    def parse(self):
        if not self.parse_line:
            return

        self.line_contents = self.parse_line.split(" ")

        last_word = self.line_contents[-1]
        if last_word in string.uppercase:
            self.parse_type = TextParseEngine.PARSE_SYMBOL
        elif last_word == "Credits":
            self.parse_type = TextParseEngine.PARSE_UNIT
        elif last_word == "?":
            self.parse_type = TextParseEngine.PARSE_ISSUE
        if self.parse_type is None:
            return
        return getattr(self, self.parse_type)()

    def parse_symbol(self):
        return self.parse_type, {self.line_contents[0]: self.line_contents[-1]}

    def parse_unit(self):
        index_is = self.line_contents.index("is")
        unit = self.line_contents[index_is - 1]
        credits_value = float(self.line_contents[index_is + 1])
        intergalactic_symbols_list = self.line_contents[:index_is - 1]
        roman_symbols = self._convert_to_romans(intergalactic_symbols_list)
        symbol_value = self._sum_roman_symbols_value(roman_symbols)
        return self.parse_type, {unit: credits_value / symbol_value}

    def parse_issue(self):
        index_is = self.line_contents.index("is")
        base_unit = self.line_contents[-2]

        if base_unit in self.parsed_units:
            intergalactic_symbols_list = self.line_contents[index_is + 1:-2]
        else:
            intergalactic_symbols_list = self.line_contents[index_is + 1:-1]
            base_unit = "Direct"
        intergalactic_symbols_str = " ".join(intergalactic_symbols_list)
        combined_unit = "||".join([base_unit, intergalactic_symbols_str])

        roman_symbols = self._convert_to_romans(intergalactic_symbols_list)
        symbol_value = self._sum_roman_symbols_value(roman_symbols)

        return self.parse_type, {combined_unit: symbol_value}

    def _convert_to_romans(self, intergalactic_symbols_list):
        roman_symbols = []
        for symbol in intergalactic_symbols_list:
            if not symbol in self.parsed_symbols:
                logging.error("You have wrong intergalactic symbol:'{}' or wrong space between, "
                              "Line Number {}, please check "
                              "it".format(symbol, self.parse_line_number))
                sys.exit(1)
            roman_symbols.append(self.parsed_symbols.get(symbol))
        return roman_symbols

    def _sum_roman_symbols_value(self, roman_symbols):
        """
        1, The symbols "I", "X", "C", and "M" can be repeated three times in succession, but no more. 
              (They may appear four times if the third and fourth are 
              separated by a smaller value, such as XXXIX.) 
        2, "D", "L", and "V" can never be repeated. 
        3, "I" can be subtracted from "V" and "X" only. 
        4, "X" can be subtracted from "L" and "C" only. 
        5, "C" can be subtracted from "D" and "M" only. 
        6, "V", "L", and "D" can never be subtracted. 
        7, Only one small-value symbol may be subtracted from any large-value symbol. 
        8, A number written in Arabic numerals can be broken into digits. 
              For example, 1903 is composed of 1, 9, 0, and 3. To write the Roman numeral, 
              each of the non-zero digits should be treated separately. 
              In the above example, 1,000 = M, 900 = CM, and 3 = III. Therefore, 1903 = MCMIII.
        :param roman_symbols:  such as: ["X", "X", "I"]
        :return int, value of accumulative sum of roman symbols
        """

        len_symbols_list = len(roman_symbols)
        if len_symbols_list == 0:
            logging.error("You have no intergalactic symbols input, please check it.")
            sys.exit(1)

        elif len_symbols_list == 1:
            return ROMEN_ALAB.get(roman_symbols[0])
        else:
            successive_repeated, symbol_index = self._successive_repeated(roman_symbols)
            if successive_repeated:
                logging.error("You have successive repeated '{}' at Line Number {}, "
                              "please check it. "
                              "".format(self.symbols_roman.get(roman_symbols[symbol_index]),
                                        self.parse_line_number))
                sys.exit(1)

            values = self._get_accumulative_symbols_values(roman_symbols)
            if not values:
                logging.error("Please check whether symbols are placed in order of value "
                              "or not, Line Number "
                              "{}".format(self.symbols_roman.get(roman_symbols[symbol_index]),
                                          self.parse_line_number))
                sys.exit(1)

            return values

    def _get_accumulative_symbols_values(self, roman_symbols):
        """
        to calculate accumulative sum of list of roman symbols
        :param roman_symbols: list, like ["X", "X"]
        :return: int, value of accumulative sum of list of roman symbols
        """
        values = []
        continue_flag = False
        for index, symbol in enumerate(roman_symbols):
            if continue_flag:
                continue_flag = False
                continue

            try:
                next_symbol = roman_symbols[index + 1]
            except Exception as e:
                next_symbol = ""
            if not next_symbol:
                values.append(ROMEN_ALAB.get(symbol))
                break

            if ROMEN_ALAB.get(symbol) >= ROMEN_ALAB.get(next_symbol):

                values.append(ROMEN_ALAB.get(symbol))

            else:
                if "".join([symbol, next_symbol]) not in ROMEN_ALAB:
                    logging.error("Symbol '{}' after '{}' is not allowed, Line Number {}, "
                                  "please check it.".format(self.symbols_roman.get(next_symbol),
                                                            self.symbols_roman.get(symbol),
                                                            self.parse_line_number))
                    sys.exit(1)
                value = ROMEN_ALAB.get(next_symbol) - ROMEN_ALAB.get(symbol)
                values.append(value)
                continue_flag = True

        copy_values = copy.deepcopy(values)
        # ensure values are right order
        if values != sorted(copy_values, reverse=True):
            values = []

        return sum(values)

    @staticmethod
    def _successive_repeated(roman_symbols):
        """
        deal with successive repeated symbols, ensure right successive repeated
        :param roman_symbols: list, like ["X", "X"]
        :return: tuple of successive_flag(bool) and symbol_index(int)
        """
        successive_flag = False
        symbol_index = -1
        for index, symbol in enumerate(roman_symbols):
            if symbol in NO_REPEATED_SYMBOLS:
                try:
                    next_symbol = roman_symbols[index + 1]
                except Exception as e:
                    next_symbol = ""
                if symbol != next_symbol:
                    successive_flag = False
                else:
                    successive_flag = True
                    symbol_index = index
            if symbol in REPEATED_SYMBOLS:
                try:
                    # just test next third value from current value of roman_symbols
                    roman_symbols[index + 3]
                except Exception as e:
                    next_successive_symbols = []
                else:
                    next_successive_symbols = roman_symbols[index:index + 4]
                if len(set(next_successive_symbols)) == 1:
                    successive_flag = True
                    symbol_index = index
                else:
                    successive_flag = False
            if successive_flag:
                break
        return successive_flag, symbol_index


class BaseEngine(object):
    def __init__(self):
        self.input_file = args.input_file
        self.input_file_md5 = None
        self.parsed_symbols = {}
        self.parsed_units = {}
        self.parsed_issues = []

    @property
    def is_file_exists(self):
        return os.path.isfile(self.input_file)

    def get_file_md5(self):
        if not self.is_file_exists:
            logging.error("Please give right input_file path and name")
            sys.exit(1)
        f = open(self.input_file, 'rb')
        contents = f.read()
        f.close()
        return hashlib.md5(contents).hexdigest()

    def is_file_changed(self):
        input_file_md5 = self.get_file_md5()
        if self.input_file_md5 != input_file_md5:
            logging.info("input file changed...")
            self.input_file_md5 = input_file_md5
            return True
        else:
            return False

    def parse_file(self):
        with open(self.input_file, 'r') as f:
            lines = f.readlines()
        for parse_line_number, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue
            text_parse_engine = TextParseEngine(line, parse_line_number,
                                                self.parsed_symbols, self.parsed_units)
            result = text_parse_engine.parse()
            if not result:
                logging.error("Can not parse Line Number {}, please check it".format(parse_line_number))
                continue
            parse_type, data = result
            if parse_type == TextParseEngine.PARSE_SYMBOL:
                self.parsed_symbols.update(data)
            elif parse_type == TextParseEngine.PARSE_UNIT:
                self.parsed_units.update(data)
            elif parse_type == TextParseEngine.PARSE_ISSUE:
                self.parsed_issues.append(data)


class ConvertCalculatorEngine(BaseEngine):
    def __init__(self):
        super(ConvertCalculatorEngine, self).__init__()

    def start(self):
        logging.info("Converting calculator starting...")
        while True:
            time.sleep(1)
            if not self.input_file_md5:
                self.input_file_md5 = self.get_file_md5()
                self.parse_file()
            else:
                if self.is_file_changed():
                    self.restart()
                else:
                    continue

            self.print_output()

    def restart(self):
        self.input_file = args.input_file
        self.input_file_md5 = None
        self.parsed_symbols = {}
        self.parsed_units = {}
        self.parsed_issues = []
        self.start()

    def print_output(self):
        for issue in self.parsed_issues:
            combined_unit, value = issue.popitem()
            unit, symbol_value = combined_unit.split("||")
            if unit in self.parsed_units:
                total_credits = value * self.parsed_units.get(unit)
                print("{} is {} Credits".format(symbol_value, str(total_credits)))
            else:
                print("{} is {}".format(symbol_value, value))


if __name__ == "__main__":
    convert_calculator = ConvertCalculatorEngine()
    convert_calculator.start()
