import socket
import pygame
import sys
import math
import numpy as np
import threading

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
# My public IP: 171.224.2.202
#  127.0.0.1

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Connect 4 - Player")

myfont = pygame.font.SysFont("monospace", 75)
small_font = pygame.font.SysFont("monospace", 30)

player_id = 0
current_turn = 1
board = np.zeros((ROW_COUNT, COLUMN_COUNT))
game_over = False
client_socket = None

def draw_board():
    screen.fill(BLACK)
    
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, 
                              (int(c * SQUARESIZE + SQUARESIZE / 2), 
                               int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), 
                              RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, 
                                  (int(c * SQUARESIZE + SQUARESIZE / 2), 
                                   height - int(r * SQUARESIZE + SQUARESIZE / 2)), 
                                  RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, 
                                  (int(c * SQUARESIZE + SQUARESIZE / 2), 
                                   height - int(r * SQUARESIZE + SQUARESIZE / 2)), 
                                  RADIUS)
    
    if not game_over:
        if current_turn == player_id:
            turn_text = f"Your turn (Player {player_id})"
            color = RED if player_id == 1 else YELLOW
        else:
            turn_text = f"Waiting for Player {current_turn}"
            color = WHITE
        text_surface = small_font.render(turn_text, True, color)
        screen.blit(text_surface, (10, 10))
    
    pygame.display.update()

def connect_to_server(server_ip='127.0.0.1', port=12345):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip, port))
        return sock
    except Exception as e:
        print(f"Connection error: {e}")
        show_error_message(f"Cannot connect to server at {server_ip}")
        return None

def show_error_message(msg):
    screen.fill(BLACK)
    text = small_font.render(msg, True, RED)
    screen.blit(text, (width//2 - text.get_width()//2, height//2))
    pygame.display.update()
    pygame.time.wait(3000)

def receive_updates():
    global board, current_turn, game_over, player_id
    
    while not game_over and client_socket:
        try:
            data = client_socket.recv(1024).decode('utf-8').strip()

            if not data:
                break

            if data.startswith("board:"):
                parts = data.split(":")
                board = np.array(eval(parts[1]))
                current_turn = int(parts[2])
                draw_board()
                
            elif data.startswith("win:"):
                winner = int(data[4:])
                game_over = True
                
                if winner == player_id:
                    message = "You win!!"
                    color = RED if player_id == 1 else YELLOW
                else:
                    message = f"Player {winner} wins!"
                    color = RED if winner == 1 else YELLOW
                
                label = myfont.render(message, 1, color)
                screen.blit(label, (width//2 - label.get_width()//2, 10))
                pygame.display.update()
                
            elif data == "your_turn":
                current_turn = player_id
                draw_board()
                
            elif data.startswith("wait:"):
                current_turn = int(data[5:])
                draw_board()
                
            elif data == "opponent_disconnected": 
                game_over = True
                show_error_message("Opponent disconnected!")
                
            elif data == "server_shutdown":
                game_over = True
                show_error_message("Server has shut down")
                
        except Exception as e:
            print(f"Error receiving data: {e}")
            game_over = True
            show_error_message("Connection lost!")
            break

def show_connection_screen():
    screen.fill(BLACK)
    draw_text("Connect 4 Online", small_font, WHITE, screen, width//2 - 100, 100)
    draw_text("Enter server IP:", small_font, WHITE, screen, width//2 - 100, 200)
    
    input_box = pygame.Rect(width//2 - 100, 250, 200, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = '127.0.0.1'
    
    while True:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
                    
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                        
        screen.fill(BLACK)
        draw_text("Connect 4 Online", small_font, WHITE, screen, width//2 - 100, 100)
        draw_text("Enter server IP:", small_font, WHITE, screen, width//2 - 100, 200)
        
        txt_surface = small_font.render(text, True, color)
        width_txt = max(200, txt_surface.get_width()+10)
        input_box.w = width_txt
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)
        
        pygame.display.flip()

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def main():
    global player_id, current_turn, game_over, client_socket
    
    server_ip = show_connection_screen()
    if not server_ip:
        return
        
    client_socket = connect_to_server(server_ip)
    if not client_socket:
        return
        
    try:
        player_id = int(client_socket.recv(1024).decode('utf-8'))
        print(f"You are Player {player_id}")
        
        threading.Thread(target=receive_updates, daemon=True).start()
        
        draw_board()
        
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    break
                    
                if event.type == pygame.MOUSEMOTION and current_turn == player_id:
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                    posx = event.pos[0]
                    if 0 <= posx <= width:
                        pygame.draw.circle(screen, RED if player_id == 1 else YELLOW, 
                                          (posx, int(SQUARESIZE/2)), RADIUS)
                    pygame.display.update()
                    
                if event.type == pygame.MOUSEBUTTONDOWN and current_turn == player_id:
                    posx = event.pos[0]
                    col = int(math.floor(posx / SQUARESIZE))
                    
                    if 0 <= col < COLUMN_COUNT:
                        try:
                            client_socket.send(str(col).encode('utf-8'))
                        except:
                            show_error_message("Connection lost!")
                            game_over = True
                            
    finally:
        if client_socket:
            client_socket.close()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()