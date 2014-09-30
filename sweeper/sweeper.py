import random

class Map():
    def __init__(self,x,y,num):
        self.length = x
        self.width = y
        self.mine = num
        self.mark = []
        
    def build_map(self):
        map_list = []
        column = self.length
        row = self.width
        for n in range(row):
            map_list.append([])
            for m in range(column):
                if (n < 9) and (m == 0):
                    map_list[n].append("   ▨")
                else:
                    map_list[n].append("  ▨")
            
        self.mark = map_list
        
                 
    def display(self):
        column = self.length
        row = self.width
        head = "  "
        for i in range(column + 1):
            if (i < 9 and i < self.length):
                head = head + "  " + str(i+1)
            elif i < self.length:
                head = head + " " + str(i+1)
        print(head)
            
        for n in range(row):
            plot = str(n+1)
            for m in range(column):
                plot += self.mark[n][m]
            print(plot)
            

def random_set(Map):
    mine_list = []
    y = Map.length
    x = Map.width
    i = 0
    while (i < Map.mine):
        x1 = random.randint(0,x-1)
        y1 = random.randint(0,y-1)
        if [x1,y1] not in mine_list:
            mine_list.append([x1,y1])
            i += 1
    
    return mine_list

def search(Map,mine_list,x_i,y_i,flag):
    y = Map.length
    x = Map.width   
    if not ((0 <= x_i <= x - 1) and (0 <= y_i <= y -1)):
        print("the number is invalid,try again please.")
        return 1
    if flag:
        return set_flag(Map,x_i,y_i)
     
     # hit the mine   
    elif [x_i,y_i] in mine_list:
        if "◤" not in Map.mark[x_i][y_i]:
            copy = Map.mark[x_i][y_i].replace("▨","※")
        else:
            copy = Map.mark[x_i][y_i].replace("◤","※")
        
        Map.mark[x_i][y_i] = copy
        all_mine(Map,mine_list)
       
        return 2
    
    #safe
    else:
        query = bulid_query(x_i,y_i,x,y)
        query = valid_query(Map,query)
        
       
        num = check(mine_list,query)
        if num == 0:
            if "◤" not in Map.mark[x_i][y_i]:
                copy = Map.mark[x_i][y_i].replace("▨","□")
            else:
                copy = Map.mark[x_i][y_i].replace("◤","□")
            Map.mark[x_i][y_i] = copy 
           
            #query = valid_query(Map,query)
            remove(Map,mine_list,query,x,y)
            
            return 0
        
        else:
            
            if "◤" in Map.mark[x_i][y_i]:
                copy = Map.mark[x_i][y_i].replace("◤",str(num))
            elif "▨" in Map.mark[x_i][y_i]:
                copy = Map.mark[x_i][y_i].replace("▨",str(num))
            else:
                print("you have search this plot, please try agian.")
                return 1
            Map.mark[x_i][y_i] = copy               
            return  0     
        
def set_flag(Map,x_i,y_i):
    if "▨" in Map.mark[x_i][y_i]:
        copy = Map.mark[x_i][y_i].replace("▨","◤") 
        Map.mark[x_i][y_i] = copy
       
        return 0
    else:
        print("Invalid input,try again please.")
        return 1
    
def count_mine(Map):
    y = Map.length
    x = Map.width
    mine = Map.mine
    count = 0
    for n1 in range(x):
        for m1 in range(y):
            if "◤" in Map.mark[n1][m1]:
                count += 1
    
    return (Map.mine - count)
            
    
    
    
'''helper function for search'''
def bulid_query(x_i,y_i,x,y):
    x_plus = x_i+1
    if x_plus >= x:
        x_plus = -1
    y_plus = y_i+1
    if y_plus >= y:
        y_plus = -1    
    x_minus = x_i-1
    y_minus = y_i-1
    
    query = [[x_i,y_plus], [x_i,y_minus], [x_plus,y_minus], [x_minus,y_minus], [x_minus,y_plus], [x_plus,y_plus], [x_plus,y_i],[x_minus,y_i]] 
    return query 

def valid_query(Map,query):
    data = []
    for i in range(len(query)):
        if -1 not in query[i]:
            data.append(i)
    copy = []
    for n in data:
        copy.append(query[n])
  
            
    query = copy
    return query

def remove(Map,mine_list,query,x,y):
    if len(query) <= 0:
        return False
    copy  = []
    for plot in query:
        a = plot[0]
        b = plot[1]
        if "▨" in Map.mark[a][b]:
            num = remove_search(Map,mine_list,x,y,a,b)
            query = bulid_query(a,b,x,y)
            query = valid_query(Map,query)            
            if num == 0:
                copy = Map.mark[a][b].replace("▨","□") 
                Map.mark[a][b] = copy
                
                remove(Map,mine_list,query,x,y)
           
            else:
                copy = Map.mark[a][b].replace("▨",str(num))
                Map.mark[a][b] = copy
                
            

def remove_search(Map,mine_list,x,y,a,b):
    query = bulid_query(a,b,x,y)
    query = valid_query(Map,query)
    if len(query) > 0:
        num = check(mine_list,query)
        return num
    
'''def show_around(Map,mine_list,query,x,y):
    for plot in query:
        a = plot[0]
        b = plot[1]
        query1 = bulid_query(a,b,x,y)
        query1 = valid_query(Map,query1)
        copy = Map.mark[a][b].replace("▨",str(check(mine_list,query)))'''
        
        
    

def all_mine(Map,mine_list):
    '''show all mine'''
    for plot in mine_list:
        x = plot[0]
        y = plot[1]
        if "◤" not in Map.mark[x][y]:
            copy = Map.mark[x][y].replace("▨","※")
        else:
            copy = Map.mark[x][y].replace("◤","※")
        Map.mark[x][y] = copy

def master(Map,mine_list):
    '''show all mine'''
      
    for plot in mine_list:
        x = plot[0]
        y = plot[1]
        copy = Map.mark[x][y].replace("▨","◤")
        Map.mark[x][y] = copy
    Map.display()
    
        
def check(mine_list,query):
    num = 0
    for plot in query:
        #if -1 not in plot:
        if plot in mine_list:
            num += 1
    return num
        

def success(Map,mine_list,mine):
    if mine == 0:
        s = 0
        for row in Map.mark:
            if "▨" in row:
                s = 1
                break
        if (s == 0):
            return True
        else:
            return False
    
                

def command(rank,x,y,mine):
    if rank == "e":
        m = Map(5,10,5)
    elif rank == "n":
        m = Map(10,20,20)
        
    elif rank == "h":
        m = Map(20,40,80)    
    
    else:
        if x >1 and y > 1 and mine > 0:
            if x < 100 and y <100:
        
                if mine <= (x*y):
                    m = Map(x,y,mine)
        else:
            print("Invalid input, please try again")
            return 0
            
        
    mine = m.mine
    m.build_map()
    m.display()
    mine_list = random_set(m)
    #print(mine_list)
    succ = 0
    turn = 0
       
    while (succ != 2):
        print("\nwhere do you want to search?(eg.2,4) Or press‘f' for flag, 'q' for quit.")
        f = 0
        a= input()
        if a == "master":
            master(m,mine_list)
            print("you win!")
            break
        if a != "f" and a != "q":
            try:
                x = int(a.split(",")[0].strip())
                y = int(a.split(",")[1].strip())
            
            except:
                print("Invalid input,try again please.")
                f = 1
               
            if f == 0:
                succ = search(m,mine_list,y-1,x-1,False)
                
                if succ != 1:
                    m.display()
                    turn += 1
                    if succ == 2:
                        print("Game over.")
                        print("you are dead,huh.")
                        return
                    
           
        if a == "f":
            print("Where do you want to put the flag?")
            k = 1
            while k == 1:
                flag_input= input()
                   
                try:
                    x = int(flag_input.split(",")[0].strip())
                    y = int(flag_input.split(",")[1].strip())
                    k = 0
                               
                except:
                    print("Invalid input,try again please.")
               
            mine1 = search(m,mine_list,y-1,x-1,True)
            if mine1 == 0:   
                
                turn += 1
            else:
                print("invalid input,please try again.")
            m.display()
                
            
        elif a == "q":
            break
        if not success(m,mine_list,count_mine(m)):
            print("Turn:",turn, "Mine", count_mine(m))
        else:
        
            print ("You win!Total turn is",turn)     
            return 1
    return 1
        
        
           
        
def start():
    flag = 0
    print("Welcome to Minesweeper")
    while flag == 0:
        user = input("\nchoose the rank(e.g. 'e' for easy,  'n' for normal,'h' for hard) \nor custom by yourself(length,width,num of mine)\nor'q' for quit\n")
        
            
        if user.isalpha():
            if user == 'q':
                
                break
            elif user == "e" or user == "n" or user == "h":
                value = command(user,0,0,0)
                if value != 0:
                    user = input("'a' for play again, else for quit.\n")
                    if user != "a":
                        flag = 1                   
            else:
                print("Invalid input, please try again.")
                continue
        else:
            try:
                lst = user.split(",")
                x = int(lst[0].strip())
                y = int(lst[1].strip())
                mine = int(lst[2].strip())
                
            except:
                print("Invalid input,try again please.")
                continue
            if x >0 and y > 0 and mine > 0:
                    
                if mine <= (x*y):
                    m = Map(x,y,mine)
                    command(0,x,y,mine)
                    user = input("press 'a' for play again, else for quit.\n")
                    if user != "a":
                        flag = 1                    
                else:
                    print("Invalid input, please try again.\n")
                                
    print("Thank you!")
    
if __name__ == "__main__":
    start()