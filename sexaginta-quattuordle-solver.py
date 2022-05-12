import urllib.request as urlr
import urllib.error as urle
import ssl
from tempfile import gettempdir
from time import perf_counter
from selenium import webdriver

#You will need to have downloaded the driver for your browser
#If you have added the browser driver to your PATH, then the code will function fine as is.
#If you have *not* added the browser driver folder to your PATH, then you can paste in the full file directory (with file name and type at the end) below.
browser_exec_path = None #r'insert_driver_path_here'
browser = 'Firefox' #Must be name in ['Edge', 'Ie', 'Chrome', 'Firefox']
#Also note that I've only tested this program in Firefox and Edge, I have no clue how well it runs in any other browsers

# file_address = r'C:\Users\Arden\Documents\Coding Projects\64ordle_'
file_address = gettempdir() + r'\64ordle_'
html_file = file_address + 'run.html'

def get_site(url):
    'Grabs the 64ordle html/js source code, modifies it, then saves as a local .html file'
    global content_str

    ssl._create_default_https_context = ssl._create_unverified_context
    content_str = urlr.urlopen(url).read().decode() #The html/js source code of the website, as decoded str

    #In order to run this program, we take the source code and modify it, adding in our own js function
    insert_index = content_str.index("function update_local_storage() {")
    content_str = content_str[:insert_index] + """//A function used by the 64ordle solver to retrieve the current state of every non-blank cell
function fetch_cells() {
 var cell_states = [];

 for(var box = 0; box < TOTAL_BOXES; box++) {
  cell_states.push([]); //add new array for each box
  for(var column = 0; column < TOTAL_COLUMNS; column++) {
   cell_states[box].push([]); //add new array for each column in this box
   for(var line = 0; line < TOTAL_LINES; line++) {
    if (line < guesses.length) { //Don't want to read information from tons of empty cells...
     var el = acquireBox(box, line, column);
     var color = el.style.backgroundColor.toString().slice(6, -1);
     var letter = guesses[line][column];
     cell_states[box][column].push([line, letter, color]); //add a new array for each cell in this column of this box
    }
   }
  }
 }
 return cell_states
}

""" + content_str[insert_index:]

    insert_index = content_str.index("function update_local_storage() {")
    insert_index = [insert_index, content_str[insert_index:]]
    insert_index[1] = insert_index[1].index("\n  } catch (e) {")
    insert_index = insert_index[0] + insert_index[1] + 1
    content_str = content_str[:insert_index] + """
   window.localStorage.setItem('answer_correct', answer_correct.join(","));

""" + content_str[insert_index:]

    # txt = open(file_address + 'read.txt', 'w')
    html = open(html_file, 'w')
    for i in [html]:#, txt]:
        i.write(content_str)
        i.close()

def setup():
    'Gathers all required information, prepares html file, opens browser'
    global headless
    global hard
    global poss_words
    global driver
    
    headless = input("Run in the background? Y/N - ")
    while headless not in ['Y', 'N', 'y', 'n', 'yes', 'no', 'Yes', 'No']:
        headless = input("Run in the background? Answer must be yes or no - ")
    if headless in ['Y', 'y', 'yes', 'Yes']: headless = True
    else: headless = False

    hard = input("Solve on hard mode instead of normal difficulty? Y/N - ")
    while hard not in ['Y', 'N', 'y', 'n', 'yes', 'no', 'Yes', 'No']:
        hard = input("Solve on hard mode instead of normal difficulty? Answer must be yes or no - ")
    if hard in ['Y', 'y', 'Yes', 'yes']: hard = True
    else: hard = False

    url = 'https://64ordle.au/?mode=daily'
    if hard: url = url + '_hard'

    get_site(url)

    normal_words = content_str[content_str.index('answer_words = "'):]
    normal_words = normal_words[normal_words.index('"') + 1:normal_words.index('"\n')]
    normal_words = normal_words.split(' ')

    poss_words = normal_words.copy()

    if hard:
        hard_words = content_str[content_str.index('hard_words = "'):]
        hard_words = hard_words[hard_words.index('"') + 1:hard_words.index('"\n')]
        hard_words = hard_words.split(' ')
        for word in hard_words: poss_words.append(word)
    
    assert browser in ['Edge', 'Ie', 'Chrome', 'Firefox'], ("Invalid browser name: " + str(browser))

    if browser == 'Edge':
        d_options = webdriver.EdgeOptions()
        if headless: d_options.headless = True
        if browser_exec_path is not None: driver = webdriver.Edge(executable_path=browser_exec_path, options=d_options)
        else: driver = webdriver.Edge(options=d_options)
    elif browser == 'Ie': #Stands for Internet Explorer
        d_options = webdriver.IeOptions()
        if headless: d_options.headless = True
        if browser_exec_path is not None: driver = webdriver.Ie(executable_path=browser_exec_path, options=d_options)
        else: driver = webdriver.Ie(options=d_options)
    elif browser == 'Chrome':
        d_options = webdriver.ChromeOptions()
        if headless: d_options.headless = True
        if browser_exec_path is not None: driver = webdriver.Chrome(executable_path=browser_exec_path, options=d_options)
        else: driver = webdriver.Chrome(options=d_options)
    elif browser == 'Firefox':
        d_options = webdriver.FirefoxOptions()
        if headless: d_options.headless = True
        if browser_exec_path is not None:
            driver = webdriver.Firefox(executable_path=browser_exec_path, service_log_path=gettempdir() + r'\geckodriver.log', options=d_options)
        else: driver = webdriver.Firefox(service_log_path=gettempdir() + r'\geckodriver.log', options=d_options)

    driver.get(html_file) #Opens our custom html file in the browser window

    if not driver.execute_script("return (typeof(Storage) !== 'undefined')"): raise AttributeError("Browser does not support Local Storage")
    else: print ("Local Storage enabled")

def printcond(item):
    'Debug function, prints whatever the input value is if the given condition is true'
    # cond = completed.count(-1) == 1 #cond should always resolve to a boolean value
    cond = False #Disables the function without me having to go through and delete every function call
    if cond: print (item)

def guess(firstcall=False):
    global before
    global correct_answers
    global completed
    if not firstcall:
        #Remember, cell_states is list in form [box, ...] with boxes as [column, ...] and columns as [[line, letter, color], ...]
        cell_states = driver.execute_script("return fetch_cells()")
        guesses = {'sure':'', 'unscramble':[], 'more_info_needed':[]}

        #How many words have we correctly solved so far?
        completed = driver.execute_script("return localStorage.getItem('answer_correct')")
        completed = completed.split(',')
        for ind, item in enumerate(completed): completed[ind] = int(item)

        #Was the last guess correct?
        if (completed.count(-1) == before[0]):
            if 0 < before[2] < 6: print ("Guess set at position " + str(before[2]) + " was not correct, box was " + str(before[1]))
            else: print ("Guess set at position " + str(before[2]) + " was not correct")
            #Note: before[2] is intended to serve as a marker to indicate which process decided that that word would be the one to be entered
            if len(correct_answers) > 0: correct_answers.pop(-1)
        before[0] = completed.count(-1)

        if not hard: prev_guesses = driver.execute_script("return localStorage.getItem('daily_guesses')")
        else: prev_guesses = driver.execute_script("return localStorage.getItem('daily_guesses_hard')")
        
        for ind, box in enumerate(cell_states):
            if completed[ind] >= 0: continue #Skips the box if it's already been solved
            blacks = {} #Letters not in the word (or letter was guessed twice in the same line and the letter's only in that line once)
            yellows = {} #Letters that are in the word but in the wrong place, records list of wrong places with each letter as key
            greens = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}} #Correctly placed letters, sorted by column
            
            for ind2, column in enumerate(box): #Collect all the cells in this box and their current status, update color dicts accordingly
                for cell in column:
                    assert cell[2] in ['green', 'yellow', 'black'], "Invalid color '" + str(cell[2]) + "'"
                    if cell[2] == 'green':
                        if cell[1] not in greens[ind2].keys(): greens[ind2][cell[1]] = []
                        greens[ind2][cell[1]].append(cell[0])
                    elif cell[2] == 'yellow':
                        if cell[1] not in yellows.keys(): yellows[cell[1]] = {ind2:[cell[0]]}
                        else:
                            if ind2 not in yellows[cell[1]].keys(): yellows[cell[1]][ind2] = []
                            yellows[cell[1]][ind2].append(cell[0])
                    elif cell[2] == 'black':
                        if cell[1] not in blacks.keys(): blacks[cell[1]] = []
                        if ind2 not in blacks[cell[1]]: blacks[cell[1]].append(ind2)
            
            if len([v for v in greens.values() if len(v) > 0]) == 5: #If we've got 5 greens
                for v in greens.values(): #Convert the greens dict into a string
                    for k in v.keys():
                        guesses['sure'] = guesses['sure'] + k[0]
                before[1] = ind #Update the before list so it describes our new guess
                before[2] = 1
                break #If we're dead certain of a guess, no more need to comb through the rest of the board

            elif len(yellows) > 0 or len([v for v in greens.values() if len(v) > 0]) > 0: #Checks the box isn't entirely black
                letters = {'green':{}, 'yellow':{}}
                for d in greens.values():
                    if len(d) > 0:
                        for a in d.items():
                            letters['green'][a[0]] = a[1]

                for k in yellows.keys():
                    if k in letters['green'].keys():
                        #If the letter's already in letters['green'] then ideally we'd skip
                        #But it's possible that there are two of the same letter in the same line
                        for kv in yellows[k].items():
                            for line in kv[1]: #kv[1] is a list of all lines where the key we're checking was yellow
                                if line in letters['green'][k]: #If the yellow instance was on the same line as the green instance
                                    if k not in letters['yellow'].keys(): letters['yellow'][k] = []
                                    letters['yellow'][k].append(kv[0])
                    else:
                        if k not in letters['yellow'].keys(): letters['yellow'][k] = []
                        for c in yellows[k].keys(): #For each column the letter is yellow in, add to the list
                            letters['yellow'][k].append(c)

                poss_guess = []
                poss_letters = []
                for l in [[key for key in k.keys()][0] for k in greens.values() if len(k) > 0]:
                    for c in greens.items():
                        if l in c[1].keys():
                            poss_guess.append((c[0], l))
                            poss_letters.append(l)
                            break
                for l in letters['yellow'].keys():
                    if l in letters['green'].keys():
                        green_lines = letters['green'][l]
                        yellow_lines = []
                        for c in letters['yellow'][l]: yellow_lines = yellow_lines + yellows[l][c]
                    if not (l in letters['green'].keys() and len([rl for rl in yellow_lines if rl in green_lines])):
                        poss_letters.append(l)
                        poss_guess.append((-1, l))

                poss_matches = []
                for word in poss_words:
                    ls = []
                    for l in poss_guess:
                        if l[0] >= 0 and word[l[0]] == l[1]: ls.append(l)
                        elif l[0] == -1:
                            if len(poss_letters) == 5 and word.count(l[1]) == poss_letters.count(l[1]) != 0: ls.append(l)
                            elif len(poss_letters) == 4 and word.count(l[1]) > 0: ls.append(l)
                    if len(ls) == len(poss_guess):
                        if word not in prev_guesses:
                            is_ok = True #This bit is basically an idiot check
                            for l in word:
                                if l in blacks.keys():
                                    if word.index(l) in blacks[l]: is_ok = False
                                    if l not in letters['green'].keys() and l not in letters['yellow'].keys(): is_ok = False
                            
                            if is_ok: poss_matches.append(word)
                
                printcond(poss_matches)
                
                if len(poss_matches) == 1:
                    guesses['sure'] = poss_matches[0]
                    before[1] = ind
                    before[2] = 2
                    break
                elif len(poss_matches) > 1:
                    if len(letters['yellow']) + len(letters['green']) in [4, 5]: #If we know 4 or 5 of the letters, try to unscramble it
                        guesses['unscramble'].append([poss_matches.copy(), blacks.copy(), letters.copy(), ind])
                    else: guesses['more_info_needed'].append([poss_matches.copy(), ind])

        del cell_states #Normally I don't care about deleting variables but this object's size on disk is absolutely humongous so

        if len(guesses['sure']) == 0 and len(guesses['unscramble']) > 0: #Try to unscramble the word
            for ind, box in enumerate(guesses['unscramble']):
                inval_words = [] #Removing items from a list that is currently being iterated over is a bad idea
                for word in box[0]:
                    for ind2, l in enumerate(word):
                        if ((l in box[1].keys() and not l in [gyl for gyl in list(box[2]['green'].keys()) + list(box[2]['yellow'].keys())])
                            or (l in box[2]['yellow'].keys() and ind2 in box[2]['yellow'][l])):
                            inval_words.append(word)
                            break
            
                for word in inval_words: box[0].remove(word)
                
                if len(box[0]) == 1 or (ind == len(guesses['unscramble']) - 1 and len(guesses['more_info_needed']) == 0):
                    guesses['sure'] = box[0][0]
                    before[1] = box[3]
                    before[2] = 3
                    break
        
        #If we've reached this point with no value for guesses['sure'], it's because we don't have enough information to make a confident guess
        #Here, we switch tactics to instead try to make guesses that will reveal the most information.
        #What we guess here won't necessarily be one of the 64ordle words, rather it concentrates on guessing new letters we haven't tried yet
        #If we make a good choice for our guess here, we should be able to have enough information next turn to get a sure guess.
        if len(guesses['sure']) == 0: #try to find closest matching words and then run the closest match
            for i in guesses.values():
                if isinstance(i, str): continue #Skip over guesses['sure']

                ensure_ls = [] #Letters we want to try guessing, but doesn't matter what spot in the word they're in
                ensure_ls_pos = [[], [], [], [], []] #ensure_ls but this time it does matter what spot the letter is in

                for box in i:
                    if len(box[0]) > 100: continue #Skips over boxes where the number of possible words is too long
                    printcond(box[0])

                    ls_pos = [[], [], [], [], []]
                    for word in box[0]:
                        for ind, l in enumerate(word):
                            ls_pos[ind].append(l)
                    printcond(ls_pos)
                    unsure_spots = [e for e in ls_pos if e.count(e[0]) != len(e)]
                    printcond(unsure_spots)
                    if len(unsure_spots) > 1: #If there are less than 4 greens
                        l_count = {}
                        for ind, pos in enumerate(unsure_spots):
                            for l in pos:
                                if l in l_count.keys(): continue
                                l_count[l] = [ls_pos.index(pos)]
                                for ind2, o_pos in enumerate(unsure_spots):
                                    if ind2 <= ind: continue
                                    if l in o_pos: l_count[l].append(ls_pos.index(o_pos))
                        for l in l_count.items():
                            if len(l[1]) > 1:
                                for ind in l[1]: ensure_ls_pos[ind] = l[0]
                            else: ensure_ls.append(l[0])

                    else: #All possible words have equal likelihood, so just guess the first one
                        for pos in ls_pos: guesses['sure'] = guesses['sure'] + pos[0]
                        before[1] = 0
                        before[2] = 4
                        printcond(unsure_spots)
                        break
                
                if len(guesses['sure']) > 0: break

                printcond(ensure_ls)
                printcond(ensure_ls_pos)

                for pos in ensure_ls_pos:
                    if len(pos) > 1:
                        most_req_ls = []
                        for l in ensure_ls_pos:
                            l_index = 0
                            for mrl in most_req_ls:
                                if pos.count(mrl) > pos.count(l): break
                                l_index += 1
                            most_req_ls.insert(l_index, l)
                        pos = [most_req_ls[-1]]
                
                poss_guesses = [[], [], [], [], []]
                if len(ensure_ls) > 0: with_ensure_ls = []
                for word in poss_words:
                    off_by = 0
                    score = 0
                    for ind, l in enumerate(word):
                        if len(ensure_ls_pos[ind]) > 0 and l != ensure_ls_pos[ind]: off_by += 1
                        if len(ensure_ls) > 0 and l in ensure_ls and l not in word[:ind]: score += 1
                    if off_by < 5: poss_guesses[off_by].append(word)
                    if score == 5 - len([pos for pos in ensure_ls_pos if len(pos) > 0]): with_ensure_ls.append(word)
                
                if len(ensure_ls) > 0 and len(with_ensure_ls) > 0: poss_guesses = [with_ensure_ls.copy()]

                for ind, pos in enumerate(poss_guesses):
                    if ind < 3 and 0 < len(pos) < 6:
                        guesses['sure'] = pos[0]
                        before[1] = 0
                        before[2] = 5
                        break
                
                if len(guesses['sure']) > 0: break
            
            #If no possible matches were found using the previous methods, just find out what letters we haven't used in a guess yet
            #Then find out what word(s) in the list of possible words have the most of those letters
            if len(guesses['sure']) == 0:
                poss_letters = [l for l in 'abcdefghijklmnopqrstuvwxyz'].copy()
                for l in prev_guesses:
                    if l in poss_letters: poss_letters.remove(l)
                most_diff_words = [[], [], [], [], []]
                for word in poss_words:
                    if len([l for l in word if word.count(l) > 1]) > 0: continue #Don't want same letter in word multiple times
                    score = len([l for l in word if l in poss_letters])
                    if score > 0: most_diff_words[score * -1].append(word) #most_diff_words will be sorted from most to least different
                
                prioritize_ls = [l for l in ['a', 'e', 'i', 'o', 'u', 's'] if l in poss_letters] #All priority letters in poss_letters

                for i in most_diff_words:
                    for ind, word in enumerate(i):
                        if len([l for l in word if l in prioritize_ls]) in [len(prioritize_ls), 5]: #All letters in prioritize_ls should be in the word
                            print ('Maximized for difference, word found with ' + str(5 - most_diff_words.index(i)) + ' unused letters')
                            guesses['sure'] = word
                            before[1] = 0
                            before[2] = 6
                            break
                    if len(guesses['sure']) > 0: break
                
                if len(guesses['sure']) == 0:
                    if 'wreck' in prev_guesses: before[2] = 8
                    else:
                        guesses['sure'] = 'wreck' #Usually if this code runs, it means something's gone wrong
                        before[1] = 0
                        before[2] = 7

        return guesses['sure']

    else:
        before = [64, 0, 0]
        enter_guess('penis') #Haha cock

def enter_guess(guess):
    'Takes 5 letter word (either in str or list format) and enters it into the game window'
    action = webdriver.ActionChains(driver)
    for letter in guess: action.send_keys(letter)
    action.send_keys(webdriver.Keys.ENTER)
    action.perform()

#For dev testing. The play function will automatically return once this many correct answers are found, no list of correct answers will be compiled.
#Set value to -1 to disengage and run program as normal, set to 64 to run as normal but skip compiling list of correct answers
InterruptAfter = -1

def play():
    'Main function where all actual solving is done'
    global before
    global correct_answers

    driver.find_element(value='daily').click() #Clicks button on title screen that goes to the actual game
    if not hard: completed_mode = 'daily'
    else:
        completed_mode = 'hard'
        driver.find_element(value="reset_hard").click() #Clicks the button that sets the game difficulty to hard
    print ("Solving " + driver.find_element(value='game_title').text + "\n\nEntering guess: bayou")
    
    t_begin = perf_counter()

    #First value in before is number of unsolved words
    #Second value in before is which word we were trying to solve with the most recent guess
    #Third value in before is a way to identify which process assigned the guess value
    before = [64, 0, 0]
    enter_guess('bayou')
    correct_answers = ['bayou'] #All guesses made are automatically added to this list, but if it's discovered they're not correct, they're removed

    while completed_mode not in str(driver.execute_script("return localStorage.getItem('completed')")):
        result = guess() #Should return a five character string
        if before[2] == 8:
            print ('Error: No possible guess could be found')
            if headless:
                result = input("Enter your own guess: ")
                while result not in poss_words:
                    result = input("Enter your own guess, must be valid 5 letter word: ")
            else: return
        if not isinstance(result, str) and len(result) == 5:
            raise ValueError("Invalid result value: '" + str(result) + "', this is an issue with the code.")
        

        print ("Entering guess: " + result)
        correct_answers.append(result)
        enter_guess(result)

        if InterruptAfter >= 0:
            if 64 - driver.execute_script("return localStorage.getItem('answer_correct')").count('-1') >= InterruptAfter: return
        
    t_total = str(perf_counter() - t_begin)
    t_total = [t_total[:t_total.find('.')], t_total[t_total.find('.'):]]
    t_total = str(int(t_total[0])//60) + "m " + str(int(t_total[0])%60) + t_total[1][:2] + "s"
    print (f"\n{len(correct_answers)} correct guesses made in " + t_total)

    correct_answers = str(correct_answers).replace(',', '').replace("'", '').replace("[", '').replace("]", '')
    for ind in [i + ((i + 1)//48) for i, s in enumerate(correct_answers) if s == ' ' and (i + 1) % 48 == 0]: #Reformat the str into grid
        correct_answers = correct_answers[:ind] + "\n" + correct_answers[ind:]
    correct_answers = f"{driver.find_element(value='game_title').text} Answers:\n-----\n" + correct_answers + "\n\n"
    print (correct_answers[:-1])

    #This assembles a text file (or appends to an existing one) all the correct 64ordle answers
    answers_txt = open(file_address + 'answers.txt', mode='a')
    answers_txt.write(correct_answers)
    answers_txt.close()
    print ("You can access the answers in a text document at " + file_address + 'answers.txt')

def allow_cmds():
    'For dev testing, allows script to be called via the command line while the program is running'
    while True:
        cmd = input()
        if cmd == 'close': driver.quit()
        elif cmd == 'storage':
            print (driver.execute_script("return Object.keys(localStorage)"))
            print (driver.execute_script("return localStorage.getItem('completed')"))
            # print (driver.execute_script("return fetch_cells()"))
        elif cmd == 'guess1':
            guess(firstcall=True)
        elif cmd == 'guess':
            guess()

try:
    setup()
    play()
except Exception as e: print (e) #If we "handle" the exception, then the input prompt below will prevent the window being automatically closed
#allow_cmds()

input("Press enter to quit. ")
driver.quit()
