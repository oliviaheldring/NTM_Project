#!/usr/bin/env python3

#Name: Olivia Heldring
#NetID: oheldrin
#Teamname: oheldrin (I worked alone)

#Project: Nondeterministic TM solver 

import csv
import os
import sys
from collections import deque
from tabulate import tabulate  


#Class to represent the machine and intepreting each line of the input file
class Turingmachine:
    def __init__(machine, file):
        machine.rules = {} #rules dict
        machine.input_file = file #input file

        with open(machine.input_file) as file:

            #parse input file and get all relevent information. 
            for i, line in enumerate(file):
                if i == 0: 
                    machine.name = line.split(',')[0]  #grab name of the machine

                elif i == 1:
                    machine.states = [state for state in line.rstrip().split(',') if state]  #list of states

                elif i == 2:
                    machine.sigma = [symbol for symbol in line.split(',') if symbol]  #input alphabet

                elif i == 3:
                    machine.gamma = [char for char in line.split(',') if char]  #tape alphabet

                elif i == 4:
                    machine.start = line.rstrip().split(',')[0]  #start state

                elif i == 5:
                    machine.accept = [state for state in line.rstrip().split(',') if state] #accept states

                elif i == 6:
                    machine.reject = line.rstrip().split(',')[0] #reject state

                else:
                    machine.rules_input(line.rstrip()) #transitions

#FUNCTION #1
    #This function reads the rules and splits them into their unique parts
    def rules_input(machine, rule):
        rule = rule.split(',')  #split by comma

        current_state = rule[0]  #grab current state
        if current_state not in machine.rules:  #add states not yet in rules
            machine.rules[current_state] = {}

        input_symbol = rule[1]  #grab input character
        if input_symbol not in machine.rules[current_state]:
            machine.rules[current_state][input_symbol] = []  #empty list for inputs not yet in rules
        
        #extract other key info
        next_state = rule[2]
        write = rule[3]
        movement = rule[4]
        #adds transition tuple to the list of all transiitons
        machine.rules[current_state][input_symbol].append((next_state, write, movement))


#FUNCTION #2
    # Determine all transitions
    def next_possible_transition(machine, tape):

        head = tape.head       #retrieve char under head    
        possible_moves = []  #list for all possible new tape configs
        current_state = tape.state      #retrieve current state

    # Loop through all possible transitions for the current state and head character
        for transition in machine.rules[current_state][head]:

            next_state = transition[0]      #get next state
            symbol_to_write = transition[1]  #get write symbol 
            move_direction = transition[2]  #get R or L

            #get current left and right sections of the tape
            l_section = tape.left
            r_section = tape.right
            #update head on tape
            head_position = symbol_to_write

            #Move head and recreate configuration
            if move_direction == 'R'and not r_section:
                #if not r_section:
                r_section = ['_']  #blank if no symbols on the right
                #Update Tape
                new_state = next_state
                new_left = l_section + [head]
                new_head = r_section[0]
                new_right = r_section[1:]
                updated_tape = Tape(state=new_state, left=new_left, head=new_head, right=new_right)

            if move_direction == 'L' and not l_section:
                #if not l_section:
                l_section = ['_']  #blank if no symbols on the left

                #Update Tape
                new_state = next_state
                new_left = l_section[:-1]
                new_head = l_section[-1]
                new_right = [head_position] + r_section
                updated_tape = Tape(state=new_state, left=new_left, head=new_head, right=new_right) 

            #add the new tape configuration
            possible_moves.append(updated_tape)

        return possible_moves



#FUNCTION #3
#Breadth first seach of the machine
    def BFS(self, string):
    # Initialize the tape and head position
        tape = list(string) #+ ['_']  # add blank symbol
        head_position = 0 #initialize head
        initial_state = self.start  #define initial state

    #Initial configuration
        current_level = [[("", initial_state, ''.join(tape))]]
        visited = set()
        steps = 0
        accept = False  #assume string is reject
        configurations_explored = 0  #to track all possible configs
        total_choices = 0  # To track the total number of nondeterministic choices

        all_levels = [current_level]  # List to hold levels of the tree

        while current_level and steps < 100:
            next_level = []  # To store the next level of configurations
    
            for config in current_level:
            #get current state, tape, and head position
                left, state, rest = config[0] if isinstance(config[0], tuple) else config
                tape = list(left) + list(rest)
                head_position = len(left)

            #check if we've reached the accept or reject states
                if state in self.accept:
                    accept = True
                    break
                if state in self.reject:
                    continue

            #stops from revisiting configurations
                tape_snapshot = (state, tuple(tape), head_position)
                if tape_snapshot in visited:
                    continue
                visited.add(tape_snapshot)

            #update config count 
                configurations_explored += 1

            #grab current symbol under the head
                current_symbol = tape[head_position]

            #ensure valid
                if current_symbol not in self.rules.get(state, {}):
                    continue

                # count number of transitions for the current state-symbol pair
                num_choices = len(self.rules[state][current_symbol])
                total_choices += num_choices  #add the number of choices at this step


            #generate all possible next configurations
                for next_state, write_symbol, move_direction in self.rules[state][current_symbol]:
                # copy tape and update 
                    new_tape = tape[:]
                    new_tape[head_position] = write_symbol

                #update head 
                    if move_direction == 'R':
                        new_head_position = head_position + 1
                        if new_head_position >= len(new_tape):
                            new_tape.append('_')  #expand the tape by adding blanks if needed
                    elif move_direction == 'L':
                        new_head_position = head_position - 1
                        if new_head_position < 0:
                            new_tape.insert(0, '_')  #expand the tape to the left if needed
                            new_head_position = 0
                    else:
                        raise ValueError("Invalid move direction")

                #create triple configuration
                    new_left = ''.join(new_tape[:new_head_position])
                    new_head = new_tape[new_head_position]
                    new_rest = ''.join(new_tape[new_head_position + 1:])
                    next_level.append([new_left, next_state, new_head + new_rest])

        #move on 
            if next_level:
                all_levels.append(next_level)
            current_level = next_level
            steps += 1

        #DEFINE DEPTH
        depth = len(all_levels)-1
        
        #define avg config 
        if depth > 0:
            avg_nondeterminism = configurations_explored / depth

        else: 
            avg_nondeterminism = 0

        #IF the string is accepted
        if accept:
            #SETTING UP INFO FOR DISPLAY TABLE2 for accepted strings)
            headers2 = [
                "User String", "Accepted Status", "Depth", "# Transitions", "Configs Explored", "Avg Nondeterminism"
            ]
            data2 = [
                [
                    string,
                    "Accepted",
                    depth,
                    steps,
                    configurations_explored,
                    round(avg_nondeterminism, 2) #if configurations_explored > 0 else "N/A"
                ]
            ]   
            #table to be printed if string is accepted
            table2 = tabulate(data2, headers=headers2, tablefmt="grid")
            print(table2)

        #ELSE -> STRING WAS REJECTED
        else:
            headers3 = [
                "User String", "Accepted Status", "Depth", "# Transitions", "Configs Explored", "Avg Nondeterminism"
            ]
            data3 = [
                [
                    string,
                    "Rejected",
                    depth,
                    steps,
                    configurations_explored,
                    round(avg_nondeterminism, 2) #if configurations_explored > 0 else "N/A"
                ]
            ]  
            #table to be printed if rejected 
            table3 = tabulate(data3, headers=headers3, tablefmt="grid")
            print(table3)


        print()
    #print a tree
        for level in all_levels:
            print(level)

        
    #function for summary table about machine at the top

    def display_summary_table(machine):
        data = [
            ["Name", machine.name],
            ["States", ", ".join(machine.states)],
            ["Input Alphabet (Σ)", ", ".join(machine.sigma)],
            ["Tape Alphabet (Γ)", ", ".join(machine.gamma)],
            ["Start State", machine.start],
            ["Accept States", ", ".join(machine.accept)],
            ["Reject State", machine.reject]
        ]
        table = tabulate(data, headers=["Attribute", "Value"], tablefmt="grid")
        print(table)
        print()

#class to represent the tape of the machine
class Tape:
    def __init__(machine, state, left = [], head = '_', right = []):
        machine.head = head   #current char at head
        machine.state = state  #curr state of machine
        machine.left = left #chars left of head
        machine.right = right #chars right of the head

    #string to represent outputs 
    def __str__(machine):
        return (
            f"Tape Left: {''.join(machine.left)}\n"
            f"Tape Head: {machine.head}\n"
            f"Tape Right: {''.join(machine.right)}\n"
            f"Current State: {machine.state}"
        )

  
#MAIN FUNCTION 
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: ./program <Turing machine input file>")  #ensure user inputs a file
        sys.exit(1)

    file_name = sys.argv[1]

    #check if file exists
    if not os.path.exists(file_name):
        print(f"Error: The file {file_name} does not exist.")
        sys.exit(1)


    turing_machine = Turingmachine(file_name)  #initalize machine

    # summary table of the machine
    print()
    print(f'Information on this Turing Machine')
    turing_machine.display_summary_table()


    #continue accepting user input until killed
    while True: 
        input_string = input('Give string: ')  #taken from user

        turing_machine.BFS(input_string)  #calling key function
        print('______________________________________')
        print()
