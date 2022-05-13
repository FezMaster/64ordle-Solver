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
    global headless, hard, poss_words, driver
    
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

def guess(firstcall=False):
    global before, correct_answers

    if firstcall: #Only runs if guess() executed via allow_cmds() input
        before = [64, 0, 0]
        enter_guess('penis') #Haha cock
        return

    def printcond(item):
        'Debug function, prints whatever the input value is if the given condition is true'
        # cond = completed.count(-1) == 1 #cond should always resolve to a boolean value
        # cond = ind == 1 and completed.count(-1) < 60
        cond = False #Disables the function without me having to go through and delete every function call
        if cond: print (item)

    #Remember, cell_states is list in form [box, ...] with boxes as [column, ...] and columns as [[line, letter, color], ...]
    cell_states = driver.execute_script("return fetch_cells()")

    #How many words have we correctly solved so far?
    completed = driver.execute_script("return localStorage.getItem('answer_correct')")
    completed = completed.split(',')
    for ind, item in enumerate(completed): completed[ind] = int(item)

    #Was the last guess correct?
    if (completed.count(-1) == before[0]):
        if 0 < before[2] < 4: print ("Guess set at position " + str(before[2]) + " was not correct, box was " + str(before[1]))
        else: print ("Guess set at position " + str(before[2]) + " was not correct")
        #Note: before[2] is intended to serve as a marker to indicate which process decided that that word would be the one to be entered
        if len(correct_answers) > 0: correct_answers.pop(-1)
    before[0] = completed.count(-1)

    if not hard: prev_guesses = driver.execute_script("return localStorage.getItem('daily_guesses')")
    else: prev_guesses = driver.execute_script("return localStorage.getItem('daily_guesses_hard')")

    final_guess = '' #Letters get added to this, but setting it as an empty string allows me to check if it's been filled or not
    uncertain = [] #Data for all boxes which had too many possible words
    
    for ind, box in enumerate(cell_states):
        if completed[ind] >= 0: continue #Skips the box if it's already been solved

        greens = [None, None, None, None, None] #Five values for the five columns, if green letter found, column value becomes [letter, [line, line, etc.]]
        yellows = {} #Structured as {'a':[[line, line, etc.] or None x 5 columns]}
        blacks = {} #Structured the same way as yellows

        for ind2, col in enumerate(box):
            for ind3, cell in enumerate(col):
                if cell[2] == 'green':
                    if greens[ind2] is None: greens[ind2] = [cell[1], []]
                    greens[ind2][1].append(ind3)
                elif cell[2] == 'yellow':
                    if cell[1] not in yellows.keys(): yellows[cell[1]] = [None, None, None, None, None]
                    if yellows[cell[1]][ind2] is None: yellows[cell[1]][ind2] = []
                    yellows[cell[1]][ind2].append(ind3)
                elif cell[2] == 'black':
                    if cell[1] not in blacks.keys(): blacks[cell[1]] = [None, None, None, None, None]
                    if blacks[cell[1]][ind2] is None: blacks[cell[1]][ind2] = []
                    blacks[cell[1]][ind2].append(ind3)
                else: raise ValueError(f"At box {ind} col {ind2} cell {ind3}, cell color not in ['green', 'yellow', 'black']")
        
        if len([g for g in greens if g is not None]) == 5: #If we've got five greens
            for p in greens: final_guess = final_guess + p[0] #Expand the string one letter at a time
            before[1] = ind
            before[2] = 1
            break #If we're dead certain of a guess, no need to comb through the rest of the boxes

        #If we don't have five greens, we will find a list of all the words that the box *could* be.
        #To do that, we need to know which letters should go in which places, and which letters cannot.
        
        g_word = ['', '', '', '', ''] #Will be occupied by single letters (if green)
        y_word = [[], [], [], [], []] #Will be occupied by lists (if yellow or black)
        b_word = [[], [], [], [], []]
        #This list is curious because the letters *are* at that spot, but the letters in the lists are ones we know *aren't* in that spot

        for ind2, l in enumerate(greens): #First, set all the letters we *know*
            if l is not None: g_word[ind2] = l[0]
        
        for l in yellows.items():
            for ind2, col in enumerate(l[1]):
                if col is not None: y_word[ind2].append(l[0])

            if len([i for i, e in enumerate(y_word) if l[0] in e and len(g_word[i]) == 0]) == len([i for i in g_word if len(i) == 0]) - 1:
                #That mess is basically trying to tell if there's only one possible location that the yellow letter could be in
                is_certain = True
                if l[0] in [g[0] for g in greens if g is not None]: #If the letter appears in the greens list
                    is_certain = False #It's possible the yellow instance was just a green instance but in the wrong spot
                    green_lines = {} #Key:value takes form linenumber:timesperline
                    for l_c in [g[1] for g in greens if g is not None and g[0] == l[0]]:
                        for line in l_c:
                            if line not in green_lines.keys(): green_lines[line] = 0
                            green_lines[line] += 1
                    
                    for col in l[1]:
                        if col is None: continue
                        for line in col:
                            if line in green_lines.keys() and green_lines[line] == len([m[0] for m in greens if m is not None and m[0] == l[0]]):
                                #How many times is this letter green?
                                #Does the letter still appear yellow on a line where all known green instances of it appear?
                                is_certain = True
                                break
                        if is_certain: break

                if is_certain:
                    for ind2, col in enumerate(y_word):
                        if len(g_word[ind2]) == 0 and l[0] not in col:
                            g_word[ind2] = l[0]
                            break #If statement should only return True for one item in word, therefore unnecessary to examine the rest
        
        for l in blacks.items():
            in_word = False
            #A letter could be black because it's not in the word
            #or because it's not in the word as many times as it appeared in a guess

            for col in g_word + y_word:
                if l[0] in col: #Nice thing is this works whether col is a list or a str
                    in_word = True
                    break
            
            if in_word: #Exclude it only from spots where we know the letter isn't there
                for ind2, col in enumerate(l[1]):
                    if col is not None: b_word[ind2].append(l[0])
            else: #Exclude it from the word entirely
                for col in b_word: col.append(l[0])
            
        #Now that we've finished collecting all the information about which letter should and cannot go where, we can create a list of possible answers

        poss_answers = []
        for w in poss_words:
            if w in prev_guesses: continue #Guessing the same word twice gives us no new information

            is_ok = True

            for col in y_word: #Checks that the word has all yellow letters (which we know are in there)
                for l in col:
                    if l not in w:
                        is_ok = False
                        break
                if not is_ok: break

            if is_ok:
                for ind2, l in enumerate(w):
                    if len(g_word[ind2]) > 0 and l != g_word[ind2]: is_ok = False #If it doesn't match a green letter
                    elif l in y_word[ind2] or l in b_word[ind2]: is_ok = False #If it has a letter we know isn't there

                    if not is_ok: break
            
            if is_ok: poss_answers.append(w)
        
        if len(poss_answers) == 1: #If there's only one possible match, we know what this word is!
            final_guess = poss_answers[0]
            before[1] = ind
            before[2] = 2
            break

        elif len(poss_answers) > 1: uncertain.append([ind, poss_answers])
        else: raise ValueError(f"poss_guesses for box {ind} has length zero") #This is for debugging, poss_guesses should always be > 0
    
    if len(final_guess) == 0: #If we haven't found an answer we're certain of yet, make an educated guess to narrow down possible candidates
        for box in uncertain:
            if len(box[1]) > 100: continue #Skip if too many possible answers

            req_ls = [{}, {}, {}, {}, {}] #Records what letters have appeared (and how many times) in each position
            for w in box[1]:
                for ind, l in enumerate(w):
                    if l not in req_ls[ind].keys(): req_ls[ind][l] = 0
                    req_ls[ind][l] += 1
            
            for ind, col in enumerate(req_ls):
                if len(col) == 1: continue #Means we've got a green

                most_req_l = ['-', 0] #This is just a placeholder value
                temp_col = col.copy() #Dictionary can't change size during iteration

                for l in col.items():
                    if l[1] > most_req_l[1]:
                        if most_req_l[1] > 0: temp_col.pop(most_req_l[0])
                        most_req_l = [l[0], l[1]]
                
                req_ls[ind] = temp_col.copy()
            
            w_by_score = [[], [], [], [], []]
            for w in poss_words:
                score = 0
                for ind, l in enumerate(w):
                    if l in req_ls[ind].keys(): score += 1
                if score > 0: w_by_score[score*-1].append(w)
            
            for ind, s in enumerate(w_by_score):
                if ind < 2 and len(s) < 3:
                    final_guess = s[0]
                    before[1] = box[0]
                    before[2] = 3
                    break
            
            if len(final_guess) > 0: break
    
    if len(final_guess) == 0: #If even after that we don't have any likely candidates, just form the most different word possible
        unused_ls = [l for l in 'abcdefghijklmnopqrstuvwxyz']
        for w in prev_guesses:
            for l in w:
                if l in unused_ls: unused_ls.remove(l)
        
        w_by_score = [[], [], [], [], []]
        for w in poss_words:
            score = 0
            for ind, l in enumerate(w):
                if l in unused_ls and l not in w[:ind]: score += 1
            if score > 0: w_by_score[score*-1].append(w)
        
        prioritize_ls = [l for l in ['a', 'e', 'i', 'o', 'u', 's', 'c'] if l in unused_ls] #Some of the most common letters

        for i in w_by_score:
            for ind, word in enumerate(i):
                if len([l for l in word if l in prioritize_ls]) in [len(prioritize_ls), 5]: #Maximize for letters in prioritize_ls
                    print ('Maximized for difference, word found with ' + str(5 - w_by_score.index(i)) + ' unused letters')
                    final_guess = word
                    before[1] = 0
                    before[2] = 4
                    break
            if len(final_guess) > 0: break
            
        if len(final_guess) == 0:
            if before[2] == 5: before[2] = 6
            else:
                final_guess = 'error' #Usually if this code runs, it means something's gone wrong
                before[1] = 0
                before[2] = 5
    
    return final_guess

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
    #Second value in before is which box we were trying to solve with the most recent guess
    #Third value in before is a way to identify which process assigned the guess value
    before = [64, 0, 0]
    enter_guess('bayou')
    correct_answers = ['bayou'] #All guesses made are automatically added to this list, but if it's discovered they're not correct, they're removed

    while completed_mode not in str(driver.execute_script("return localStorage.getItem('completed')")):
        result = guess() #Should return a five character string
        if before[2] == 6:
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
