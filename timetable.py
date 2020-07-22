# Author -> Abhas Jain

import glob
from collections import defaultdict
import sys
import os
import csv
from operator import itemgetter
import random


class student:
    """Definition of a student."""

    def __init__(self, rollno, name, section, dept_code, email):
        self.Rollno = rollno
        self.Name = name
        self.Section = section
        self.Dept_Code = dept_code
        self.Email = email

    def __eq__(self, other):
        return self.Rollno == other.Rollno

    def __str__(self):
        return self.Rollno + ' ' + self.Name

    def __hash__(self):
        return hash(self.Rollno)

    def __repr__(self):
        return self.Rollno + ' ' + self.Name


"""
Input is taken from a folder named - "subj_stdnts" in the same directory as this code.

The following things are implemented -
    1.) Student object whose definition is given Student.py file

    2.) getStudent mapping which returns student object from its RollNo
        Example - getStudent['17134021'] 

    2.) A mapping of subjects to students which is extracted from the csv files in the input folder.
        Subject - code is used as the key. 
        Example - subjectToStudent['MA-101'] gives a list of students registered.
  
    3.) Inverse mapping of the above mapping i.e. from student to the subjects taken.
        Student object is used as the key.
        Example - studentToSubject[getStudent['17134021']] gives the list of subjects.

    4.) indexOfSubject -> Every subject is indexed and given a unique number.
        Subject - code is used as a key.
        Example - indexOfSubject['MA-101']

    5.) Clash - Matrix (c) -> c[i][j] denotes the number of students registered for both ith and jth indexed subjects.
        It is a symmetric matrix i.e. c[i][j] = c[j][i]
"""

days = int(input("Enter number of days -> "))

# Choose number of iterations.
iterations = int(input("Enter number of iterations to perform -> "))

print("Generating Time Table...")


def read():  # To extract the input from csv
    result = {}
    directory = "subj_stdnts"
    csvfiles = glob.glob(os.path.join(directory, '*.csv'))
    for files in csvfiles:
        subject_name = files[12:files.__len__() - 4]  # course-name extracted from relative address
        result[subject_name] = []
        with open(files) as csvfile:
            reader = csv.reader(csvfile)
            fields = next(reader)  # to skip the field names
            for row in reader:
                current_student = student(row[0], row[1], row[2], row[3], row[4])
                result[subject_name].append(current_student)
    return result


subjectToStudent = read()
studentToSubject = {}  # Invert of the above mapping. Student -> Subjects.

getStudent = {}  # get the Student object from Roll No.

for subject in subjectToStudent:  # To invert above mapping
    for student in subjectToStudent[subject]:
        if student not in studentToSubject:
            studentToSubject[student] = []
            getStudent[student.Rollno] = student
        if subject not in studentToSubject[student]:
            studentToSubject[student].append(subject)

subjects_count = len(subjectToStudent)
student_count = len(studentToSubject)

rows, cols = subjects_count, subjects_count

c = [[0 for i in range(cols)] for j in range(rows)]  # Clash - Matrix

indexOfSubject = {}  # Indexing the subjects
curIndex = 0
indexToName = {}

for subject in subjectToStudent:
    indexOfSubject[subject] = curIndex
    indexToName[curIndex] = subject
    curIndex += 1

"Generating a pair of index and count of students and sorting it to choose the next best."
enrolledInSubject = [(indexOfSubject[subject], len(subjectToStudent[subject])) for subject in subjectToStudent]

enrolledInSubject.sort(key=itemgetter(1), reverse=True)  # Sorting in descending according to the number of students.

for student in studentToSubject:  # Filling the Clash - Matrix
    processedCourse = []
    for subject in studentToSubject[student]:
        currentIndex = indexOfSubject[subject]
        for previousIndex in processedCourse:
            c[currentIndex][previousIndex] += 1
            c[previousIndex][currentIndex] += 1
        processedCourse.append(currentIndex)

timeSlots = 4 * days  # (Number of examination days * 4) Every 4th index will be skipped while setting.


def cost(i, j):
    # Returns coefficient of Cost between time slots numbered i and j
    return pow(2, 7 - abs(i - j))


finalCost = 1e18  # Initial infinite value
finalSchedule = defaultdict(list)

for i in range(iterations):
    print("Iteration: ", i)
    timetable = defaultdict(list)
    totalCost = 0
    for subject in enrolledInSubject:
        # Iterating over subjects in descending order of their enrollment.
        costForExam = {}
        for choosenSlot in range(1, timeSlots):
            clash = False  # To check the no clash condition
            if choosenSlot % 4 == 0:
                continue  # This is to compensate time for shifting to next day.
            for scheduledExams in timetable[choosenSlot]:
                if c[scheduledExams][subject[0]] != 0:
                    # Exams are clashing, it cannot be scheduled.
                    clash = True
                    break
            if clash:
                continue
            currentCost = 0
            if choosenSlot not in costForExam:
                costForExam[choosenSlot] = 0
            # Calculating the incurred cost for setting an exam in a particular slot.
            for checkSlots in range(max(1, choosenSlot - 7), min(timeSlots, choosenSlot + 7)):
                for exams in timetable[checkSlots]:
                    currentCost += cost(checkSlots, choosenSlot) * c[exams][subject[0]]
            costForExam[choosenSlot] = currentCost
        takeBestSlot = [(choosenSlot, costForExam[choosenSlot]) for choosenSlot in costForExam]
        if len(takeBestSlot) == 0:
            totalCost = 1e18
            break
        # Randomly shuffling and sorting the slots in increasing order of their cost.
        random.shuffle(takeBestSlot)
        takeBestSlot.sort(key=itemgetter(1))
        # Choosing a random time slot out of top 5 choices.
        slotFinalized = takeBestSlot[random.randrange(0, min(5, len(takeBestSlot)))]
        timetable[slotFinalized[0]].append(subject[0])
        totalCost += costForExam[slotFinalized[0]]
    # If this time table is best choose it.
    if totalCost < finalCost:
        finalCost = totalCost
        finalSchedule = timetable

examsDone = 0

# If no time table is found.
if finalCost == 1e18:
    print("Unable to find")
    sys.exit()

# Printing the schedule to schedule.txt file
makefile = open("schedule.txt", 'w+')

for slot in range(1, timeSlots):
    if slot % 4 == 0:
        continue
    if slot % 4 == 1:
        makefile.write("\n")
        makefile.write("DAY - " + str((slot + 3) // 4) + "-->\n")
        makefile.write("\n")
    makefile.write("SLOT - " + str(slot % 4) + "\n")
    exams = [indexToName[index] for index in finalSchedule[slot]]
    makefile.write("[")
    for i in range(len(exams)):
        makefile.write("'" + exams[i] + "'")
        if i != len(exams) - 1:
            makefile.write(", ")
    makefile.write("]\n")
