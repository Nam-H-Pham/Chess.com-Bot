from stockfish import Stockfish
import os

stockfish = Stockfish('C:\Python36_64bit\chessdotcom\stockfish-11-win\stockfish-11-win\Windows\stockfish_20011801_x64_modern.exe')
stockfish.set_fen_position("3kq3/pp6/7p/2P3p1/8/5P2/1N3PPP/1K2Q2R w KQkq - 0 1")
print(stockfish.get_best_move())
