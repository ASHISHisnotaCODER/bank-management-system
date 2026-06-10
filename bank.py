import json
import random
import string
from pathlib import Path

class Bank:
    database = Path(__file__).resolve().parent / 'data.json'       
    data = []                                                  #!  -- these two lines are very important to keep the json file in the current folder only

    try:
        if database.exists():
            with database.open() as fs:
                content = fs.read().strip()
                if content:
                    data = json.loads(content)
        else:
            print("No such file Exists !")

    except Exception as err:
        print(f"An exception occured as :- {err}")

    @classmethod
    def __update(cls):
        with cls.database.open('w', encoding='utf-8') as fs:
            json.dump(cls.data, fs, indent=4)
            
    @classmethod
    def __accountgenerate(cls):
        alpha = random.choices(string.ascii_letters,k = 3)
        num = random.choices(string.digits,k = 3)
        spchar = random.choices("!@#$%^&*",k=2)
        id = alpha + num + spchar
        random.shuffle(id)
        return "".join(id)


    @classmethod
    def update(cls):
        cls.__update()

    @classmethod
    def account_generate(cls):
        return cls.__accountgenerate()

    @classmethod
    def find_user(cls, account_number, pin):
        for user in cls.data:
            if str(user['accountNo.']) == str(account_number) and user['pin'] == pin:
                return user
        return None


    def CreateAccount(self):
        info = {
            "name" : input("Enter your name:- "),
            "age" : int(input("Enter your age:- ")),
            "email" : input("Enter your email:-"),
            "pin" : int(input("Create a pin:- ")),
            "accountNo." : Bank.__accountgenerate(),
            "balance" : 0
        }

        if info['age'] < 18 or len(str(info['pin'])) != 4:
            print("\nSorry you cannot create your account : !")
        else:
            print("\nAccount has been created successfully")
            for i in info:
                print(f"{i} : {info[i]}")
            print("\nPlease note down your account number ! \n")

            Bank.data.append(info)
            Bank.__update() 
    
    
    def DepositMoney(self):
        accountNumber = input("please tell your account number : ")
        Pin = int(input("please tell your pin : "))
        
        userdata = [i for i in Bank.data if i['accountNo.'] == accountNumber and i['pin'] == Pin]

        if userdata == False:
            print("sorry ! no data found__")
        else:
            amount = int(input("\nEnter the amount to deposite :"))
            if amount > 10000 or amount < 0:
                print("\nSorry ! The dopositable amount must be 0rs to 10000rs")
            else:
                userdata[0]['balance'] += amount
                Bank.__update()
                print("\nAmount deposited Successfully !! ")


    def WithdrawMoney(self):
        accountNumber = input("please tell your account number : ")
        Pin = int(input("please tell your pin : "))
        
        userdata = [i for i in Bank.data if i['accountNo.'] == accountNumber and i['pin'] == Pin]

        if userdata == False:
            print("sorry ! no data found__")
        else:
            amount = int(input("\nEnter the amount to Withdraw :"))
            if userdata[0]['balance'] < amount:
                print(f"\nSorry ! You have only {userdata[0]['balance']} rs in your account")
            else:
                userdata[0]['balance'] -= amount
                Bank.__update()
                print("\nAmount Withdrawal Successful !! ")


    def CheckDetails(self):
        accountNumber = input("\nplease tell your account number : ")
        Pin = int(input("please tell your pin : "))

        userdata = [i for i in Bank.data if i['accountNo.'] == accountNumber and i['pin'] == Pin]
        print("\nYour Details :-\n")
        for i in userdata[0]:
            print(f"{i} : {userdata[0][i]}")


    def UpdateDetails(self):
        accountNumber = input("please tell your account number : ")
        Pin = int(input("please tell your pin : "))
        
        userdata = [i for i in Bank.data if i['accountNo.'] == accountNumber and i['pin'] == Pin]

        if userdata == False:
            print("\nNo User Found !!")
        else:
            print("\nNote :-")
            print("You cannot change the Account number or Balance !")
            print("Fill the details for change or leave it empty if no change !\n")

            newdata = {
                "name" : input("Please Enter new name or press enter : "),
                "age" : input("Please Enter your new age or press enter : "),
                "email" : input("Please Enter your new email id or press enter : "),
                "pin" : input("Enter your new pin or press enter : ")
            }

            if newdata["name"] == "":
                newdata["name"] = userdata[0]['name']
            if newdata["age"] == "":
                newdata["age"] = userdata[0]['age']
            if newdata["email"] == "":
                newdata["email"] == userdata[0]['email']
            if newdata["pin"] == "":
                newdata["pin"] = userdata[0]['pin']

            newdata['accountNo.'] = userdata[0]['accountNo.']
            newdata['balance'] = userdata[0]['balance']
            
            if type(newdata['pin']) == str:
                newdata['pin'] = int(newdata['pin'])

            for i in newdata:
                if newdata[i] == userdata[0][i]:
                    continue
                else:
                    userdata[0][i] = newdata[i]

            Bank.__update()
            print("\nDetails Updated Successfully !\n")


    def DeleteAccount(self):
        accountNumber = input("please tell your account number : ")
        Pin = int(input("please tell your pin : "))
        
        userdata = [i for i in Bank.data if i['accountNo.'] == accountNumber and i['pin'] == Pin]

        if userdata == False:
            print("Sorry ! No such data Exists -")
        else:
            check = input("\nPress \"y\" if you want to delete Account or Press \"n\" :- ")
            if check == 'n' or check == 'N':
                print("Bypassed")
            else:
                index = Bank.data.index(userdata[0])
                Bank.data.pop(index)
                print("\nYour Account has been successfully deleted !!\n")
                Bank.__update()


if __name__ == "__main__":
    user = Bank()

    print("Press 1 for Creating an Account")
    print("Press 2 for Depositing the Money")
    print("Press 3 for Withdrawing the money")
    print("Press 4 for Details")
    print("Press 5 for Updating the Details")
    print("Press 6 for Deleting your account")

    check = int(input("\nPlease Enter Your Response:- "))

    if check == 1:
        user.CreateAccount()

    if check == 2:
        user.DepositMoney()

    if check == 3:
        user.WithdrawMoney()

    if check == 4:
        user.CheckDetails()

    if check == 5:
        user.UpdateDetails()

    if check == 6:
        user.DeleteAccount()