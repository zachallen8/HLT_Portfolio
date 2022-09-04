from distutils.command.build_scripts import first_line_re
import sys
import re
import os
import pickle
employees = ''
employeeList = []

# person class
class person():
    def __init__(self, last, first, mi, id, phone):
        self.last = last
        self.first = first
        self.mi = mi
        self.id = id
        self.phone = phone
    #display method for person class
    def display(self):
        print('Employee ID: ' + self.id)
        print(self.first + ' ' + self.mi + ' ' + self.last)
        print(self.phone)

# sysarg validator, from Dr. Mazidi's GitHub demo
def sysArgValidation(filepath):
    with open(os.path.join(os.getcwd(), filepath), 'r') as f:
        employees = f.read()
    print(employees)
    employeeList = employees.splitlines()
    #dict to return
    finalList = {}

    #loops through the list, validating input
    for i in employeeList[1:]:
        results = i.split(',')
        #input for last name
        lName = results[0]
        lName = lName.capitalize()
        #input for first name
        fName = results[1]
        fName = fName.capitalize()
        #input for middle name
        mName = results[2]
        mName = mName.upper()
        #regex for id
        id = results[3]
        while(not re.search('[A-Z][A-Z][0-9][0-9][0-9][0-9]', id)):
            print("ID invalid: " + id + "\nID is two letters followed by 4 digits")
            id = input("Please enter a valid ID: ")
        #regex for phone
        phone = results[4]
        while(not re.search('\d\d\d-\d\d\d-\d\d\d\d', phone)):
            print("Phone number " + phone + " is invalid. \nEnter phone number in form 123-456-7890")
            phone = input("Please enter phone number: ")
        if(mName == ''):
            mName = 'X'

        #adds person to list, checking if the id is a key already
        toAdd = person(lName, fName, mName, id, phone)
        if(id in finalList.keys()):
            print("This key is in the dictionary.")
            exit()
        finalList.update({id: toAdd})
    
    print("\nEmployee List:")
    #creates the pickle file
    pickle.dump(finalList, open('dict.p', 'wb'))

#main method
def main():
    if len(sys.argv) < 2:
        print('Please pass \'data/data.csv\' as a sysarg.')
        exit()
    else:
        fp = sys.argv[1]
        sysArgValidation(fp)
    #opens and prints the pickle file
    dict_in = pickle.load(open('dict.p', 'rb'))  # read binary
    values = dict_in.values()
    for i in values:
        print(" ")
        i.display()

if __name__ == "__main__":
    main()