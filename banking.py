import sqlite3
import random


class Bank:
    def __init__(self):
        self.logged = None
        self.conn = sqlite3.connect("card.s3db")
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS card (
            aid INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT UNIQUE,
            pin TEXT,
            balance INTEGER DEFAULT 0
        )""")
        self.conn.commit()

    @staticmethod
    def generate_luhn_number():
        prefix = "400000"
        digits = [int(x) for x in prefix] + [random.randint(0, 9) for _ in
                                             range(9)]  # Generate the first 10 random digits
        total = 0
        for i, digit in enumerate(digits):
            if i % 2 == 0:
                doubled = digit * 2
                total += doubled if doubled <= 9 else doubled - 9
            else:
                total += digit
        checksum = (10 - (total % 10)) % 10
        luhn_number = int("".join(map(str, digits + [checksum])))  # Append the checksum digit
        return luhn_number

    @staticmethod
    def luhn_checksum(number):
        digits = list(map(int, str(number)))
        checksum = 0
        for i in range(len(digits)):
            if i % 2 == 0:
                digit = digits[i] * 2
                checksum += digit if digit <= 9 else digit - 9
            else:
                checksum += digits[i]

        return checksum % 10 == 0

    def assign_number(self):
        while True:
            number = self.generate_luhn_number()
            if self.cur.execute("SELECT * FROM card WHERE number = ?", (number,)).fetchone() is None:
                return number

    def create_account(self, number=None, balance=0):
        pin = random.randint(1000, 9999)
        if number is None:
            number = self.assign_number()
        self.cur.execute("INSERT INTO card (number, pin, balance) VALUES (?, ?, ?)", (number, pin, balance))
        self.conn.commit()
        print("Your card has been created\nYour card number:\n{}\nYour card PIN:\n{}\n".format(number, pin))

    # def deposit(self, aid, amount):
    #     self.cur.execute("UPDATE bank SET balance = balance + ? WHERE aid = ?", (amount, aid))
    #     self.conn.commit()
    #
    # def withdraw(self, aid, amount):
    #     self.cur.execute("UPDATE bank SET balance = balance - ? WHERE aid = ?", (amount, aid))
    #     self.conn.commit()
    #
    def bank_exit(self):
        self.conn.close()
        print('Bye!')
        exit()

    def get_balance(self, number):
        self.cur.execute("SELECT balance FROM card WHERE number = ?", (number,))
        balance = self.cur.fetchone()[0]
        return balance

    def log_into_account(self, number, pin):
        self.cur.execute("SELECT * FROM card WHERE number= ?", (number,))

        acc_details = self.cur.fetchone()
        if acc_details is None or int(acc_details[2]) != pin:
            print("Wrong card number or PIN!\n")
        else:
            print("You have successfully logged in!\n")
            self.logged = True
            self.acc_menu(number)

    def add_income(self, number):
        income = int(input('Enter income:'))
        self.cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?", (income, number))
        self.conn.commit()
        print('Income was added!\n')

    def do_transfer(self, number):
        recipient = int(input('Transfer\nEnter card number:'))
        if not self.luhn_checksum(recipient):
            print('Probably you made a mistake in the card number. Please try again!')
        elif self.cur.execute("SELECT * FROM card WHERE number = ?", (recipient,)).fetchone() is None:
            print('Such a card does not exist.')
        elif recipient == number:
            print('You can\'t transfer money to the same account!')
        else:
            amount = int(input('Enter how much money you want to transfer:'))
            if amount > self.get_balance(number):
                print('Not enough money!\n')
                return
            self.cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?", (amount, recipient))
            self.cur.execute("UPDATE card SET balance = balance - ? WHERE number = ?", (amount, number))
            self.conn.commit()

    def close_account(self, number):
        self.cur.execute("DELETE FROM card WHERE number = ?", (number,))
        self.conn.commit()
        print('The account has been closed!\n')

    def acc_menu(self, number):
        while self.logged:
            match input('1. Balance\n'
                        '2. Add income\n'
                        '3. Do transfer\n'
                        '4. Close account\n'
                        '5. Log out\n'
                        '0. Exit\n'):
                case '1':
                    print("Balance: {}\n".format(self.get_balance(number)))
                case '2':
                    self.add_income(number)
                case '3':
                    self.do_transfer(number)
                case '4':
                    self.close_account(number)
                    self.logged = False
                    self.main_menu()
                case '5':
                    self.logged = False
                    print("You have successfully logged out!\n")
                    self.main_menu()
                case '0':
                    self.bank_exit()

    def main_menu(self):
        match input('1. Create an account\n2. Log into account\n0. Exit\n'):
            case '1':
                self.create_account()
            case '2':
                number = int(input('Enter your card number:'))
                pin = int(input('Enter your PIN:'))
                self.log_into_account(number, pin)
            case '0':
                self.bank_exit()


if __name__ == "__main__":
    bank = Bank()
    while True:
        bank.main_menu()
