import os
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from helium import *

from stockfish import Stockfish

import subprocess
import ctypes

from threading import Thread

import time

def get_attrs(span):
    attrs = []
    for attr in span.get_property('attributes'):
        attrs.append([attr['name'], attr['value']])
    return(attrs)

def decode_piece(src,team):
    name = src.replace('url("https://images.chesscomfiles.com/chess-themes/pieces/neo/150/','')
    name = name.replace('.png")','')
    
    if team == 'w':
        if list(name)[0] == 'w':
            name = list(name)[1].upper()
        else:
            name = list(name)[1].lower()
        return(name)
    
    if team == 'b':
        if list(name)[0] == 'b':
            name = list(name)[1].upper()
        else:
            name = list(name)[1].lower()
        return(name)

def convert_notation(data,move_num,team): #col and row data to notation

    grid = [[1]*8 for _ in range(8)]
    for i in board:
            grid[i[1]][i[0]] = i[2]

    grid_visual = [[' ']*8 for _ in range(8)]
    for i in board:
            grid_visual[i[1]][i[0]] = i[2]

    notation_list = []
    for higher_index,row in enumerate(grid):
        for i in range(8):
            for index,i in enumerate(row):
                if index != len(row)-1:
                        if type(row[index]) is int and type(row[index+1]) is int:
                                row[index] += row[index+1]
                                row.pop(index+1)
        row = "".join(str(x) for x in row)#join together (normal .join() doesnt work :()
        notation_list.append(row)
        
    notation_list = "/".join(str(x) for x in notation_list)
    #team = str(team).replace(" ", "")
    team = 'w'
    notation_list += " "+team#+" KQkq - 0 "+str(move_num)
    return (notation_list,grid_visual)

def opposite_in_list(lst,item):
    reverse_lst = lst[::-1]
    return (reverse_lst[lst.index(item)])
    
def get_move_location(locator_symbols,best_move,chessboard,team):
    team = str(team).replace(" ", "")
    vertical = ['8','7','6','5','4','3','2','1']
    horizontal = ['a','b','c','d','e','f','g','h']

    firstpart = best_move[:2]
    secondpart = best_move[-2:]

    if team == 'b':
        letter = opposite_in_list(horizontal,list(firstpart)[0])
        number = opposite_in_list(vertical,list(firstpart)[1])
        firstpart = letter+number

        letter = opposite_in_list(horizontal,list(secondpart)[0])
        number = opposite_in_list(vertical,list(secondpart)[1])
        secondpart = letter+number
    print(firstpart,secondpart)
        

    for move_location in [firstpart,secondpart]:
        for symbol in locator_symbols:
            symboltext = (symbol.text)

            if symboltext in move_location and symboltext in horizontal:
                symbolx = symbol.location['x']
                relsymbolx =  symbol.location['x'] - chessboard.location['x']

            if symboltext in move_location and symboltext in vertical:
                symboly = symbol.location['y']
                relsymboly =  symbol.location['y'] - chessboard.location['x']

        if move_location == firstpart:
            '''for span in all_chesspieces:
                #if (span.location['x'], span.location['y']) == (symbolx, symboly):
                if abs(span.location['x'] - symbolx) < 10 and abs(span.location['y'] - symboly) < 10:
                    set_driver(driver)#helium clicker
                    click(Point(symbolx+10, symboly+10))
                    print(symbolx,symboly,'first')'''
            set_driver(driver)#helium clicker
            click(Point(symbolx+10, symboly+10))
            print(symbolx,symboly,'first')
                    
        if move_location == secondpart:
            set_driver(driver)#helium clicker
            click(Point(symbolx+10, symboly+10))
            print(symbolx,symboly,'second')

def get_board(all_chesspieces, move_num):
    board = []
    for span in all_chesspieces:
        #print (span.text)
        #print(get_attrs(span))
        
        relx = span.location['x'] - chessboard.location['x'] #relative x to the board
        rely = span.location['y'] - chessboard.location['y'] #relative y

        if relx == 0:
            col = 0
        else:
            col = int(relx/span.size['width'])
        if rely == 0:
            row = 0
        else:
            row = int(rely/span.size['height'])#decode coords to row/col e.g (0,0) for a8
        
        src = span.value_of_css_property("background-image")
        peice = decode_piece(src,team)

        board.append([col,row,peice])
        #print((col,row), peice)
    return(board)
                
def get_capslock_state():
    hllDll = ctypes.WinDLL ("User32.dll")
    VK_CAPITAL = 0x14
    return hllDll.GetKeyState(VK_CAPITAL)
                
def check_for_stockfish():
    global stockfish
    s = subprocess.check_output('tasklist', shell=True)
    if b'stockfish' not in s:
        stockfish = Stockfish('C:\Python36_64bit\Projekts\chessdotcom\stockfish-9-win\stockfish-9-win\Windows\stockfish_9_x64.exe')
        stockfish.set_skill_level(2000)
        stockfish.set_depth(32)

def get_next_move():
    global stockfish, best_move
    stockfish.set_fen_position(fen_board)
    best_move = stockfish.get_best_move_time(950)#stockfish.get_best_move()
    best_move = best_move[:4]#avoid bugs
    
    
options = webdriver.ChromeOptions()
driver_path = os.path.join(os.path.dirname(__file__),"chromedriver.exe")
options.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
driver = webdriver.Chrome(executable_path=driver_path, options=options)

driver.get('https://www.chess.com/play/online')


check_for_stockfish()
while True:
    #check_for_stockfish()
    move_num = 0
    team=input('team (w/b): ')
    team = team.lower().replace(" ", "")
    if '!help' == team:
        print('- !exit')
        print('- !resetwindow')
    if '!exit' == team:#end program to debug
        sys.exit()
    if '!resetwindow' == team: #avoid 'window was already closed' error
        window_after = driver.window_handles[0]
        driver.switch_to.window(window_after)#keep to first tab
        print('window has been reset!')
    if 'w' != team and 'b' != team:#make sure viable team is given
        continue
    while True:
        q = input('next move...')
        
        if get_capslock_state()==1: #trigger caps to break loop and debug 
            break                   #or when stockfish crashes 

        try:
            check_for_stockfish()
            
            chessboard = driver.find_elements_by_id('board-layout-chessboard')[0]
            #chesspieces = driver.find_element_by_class_name('chess_com_piece')
            #all_chesspieces = driver.find_elements_by_xpath('//*[@class="piece square"]')
            all_chesspieces = driver.find_elements_by_xpath("//*[contains(@class, 'piece w')]")
            all_chesspieces.extend(driver.find_elements_by_xpath("//*[contains(@class, 'piece b')]"))

            locator_symbols = driver.find_elements_by_xpath('//*[@class="coordinate-light"]')
            locator_symbols.extend(driver.find_elements_by_xpath('//*[@class="coordinate-dark"]'))

            #print(all_chesspieces)
            
            if len(all_chesspieces) != 0:
                move_num += 1
                
                board = get_board(all_chesspieces, move_num)
                fen_board = convert_notation(board,move_num,team)[0]
                grid = convert_notation(board,move_num,team)[1]

                best_move = 'awaiting'
                while best_move == 'awaiting':
                    if get_capslock_state()==1:
                        break
                    board = get_board(all_chesspieces, move_num)
                    fen_board = convert_notation(board,move_num,team)[0]
                    grid = convert_notation(board,move_num,team)[1]
                
                    background_thread = Thread(target=get_next_move, args=())
                    background_thread.start()
                    time.sleep(1)

                #print('-'*8)  #old grid display
                #for i in grid:
                #    print (i)
                print(stockfish.get_board_visual())

                print("<<"+best_move+">>")
                print(fen_board)

            try:
                get_move_location(locator_symbols,best_move,chessboard,team)
            except Exception as e: 
                print(e)
                
        except Exception as e: 
                print(e)
        



