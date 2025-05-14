import socket
import threading
import numpy as np
import pygame
import time
from game_logic import *
from constants import *

class Connect4Server:
    def __init__(self, screen):
        self.current_player = 1
        self.game_started = False
        self.game_over = False
        self.clients = []
        self.board = create_board()
        self.screen = screen
        self.lock = threading.Lock()
        self.font = pygame.font.SysFont(FONT_NAME, 40)
        self.small_font = pygame.font.SysFont(FONT_NAME, 20)
        
    def draw_text(self, text, color, x, y):
        textobj = self.font.render(text, True, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        self.screen.blit(textobj, textrect)

    def draw_status(self):
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
        status_text = f"Player {self.current_player}'s turn" if not self.game_over else "Game over"
        text_surface = self.small_font.render(status_text, True, WHITE)
        self.screen.blit(text_surface, (10, 10))
        
        player1_text = f"Player 1 (Red) - {'Connected' if any(c['player_id']==1 for c in self.clients) else 'Disconnected'}"
        player2_text = f"Player 2 (Yellow) - {'Connected' if any(c['player_id']==2 for c in self.clients) else 'Disconnected'}"
        
        self.screen.blit(self.small_font.render(player1_text, True, RED), (WIDTH//2 - 200, 10))
        self.screen.blit(self.small_font.render(player2_text, True, YELLOW), (WIDTH//2 + 20, 10))

    def run(self):
        self.screen.fill(WHITE)
        self.draw_text("Server is starting...", BLUE, WIDTH // 2 - 100, 100)
        pygame.display.flip()
        
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', 12345))
            server_socket.settimeout(0.5)
            server_socket.listen(2)
            
            self.draw_text("Server is listening...", BLUE, WIDTH // 2 - 100, 150)
            pygame.display.flip()
            
            player_id = 1
            while len(self.clients) < 2 and not self.game_over:
                try:
                    client_socket, addr = server_socket.accept()
                    alert = f"Player {player_id} connected from {addr[0]}"
                    print(alert)
                    
                    self.clients.append({'player_id': player_id, 'socket': client_socket})
                    client_socket.send(str(player_id).encode('utf-8'))
                    
                    threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, player_id),
                        daemon=True).start()
                    
                    # self.screen.fill(WHITE)
                    draw_board(self.board, self.screen)
                    self.draw_status()
                    self.draw_text(f"Player {player_id} connected", 
                                 RED if player_id == 1 else YELLOW, 
                                 WIDTH//2 - 100, 10)
                    pygame.display.flip()
                    
                    if len(self.clients) == 2:
                        self.game_started = True
                        # self.screen.fill(WHITE)
                        draw_board(self.board, self.screen)
                        self.draw_status()
                        self.draw_text("Game started!", GREEN, WIDTH//2 - 80, 10)
                        pygame.display.flip()
                        self.update_all_clients()

                    player_id += 1

                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error: {e}")
                    break
            while not self.game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.game_over = True

            

        except Exception as e:
            print(f"Server error: {e}")
            self.draw_text(f"Server error: {str(e)}", RED, WIDTH // 2 - 150, 200)
            pygame.display.flip()
        finally:
            server_socket.close()
            self.cleanup()

    def handle_client(self, client_socket, player_id):
        try:
            while not self.game_started and not self.game_over:
                time.sleep(0.1)
            
            while not self.game_over:
                if self.current_player == player_id:
                    client_socket.send("your_turn".encode('utf-8'))
                    
                    data = client_socket.recv(1024).decode('utf-8').strip()
                    if not data:
                        break
                    
                    try:
                        col = int(data)
                        if self.process_move(col, player_id):
                            # self.screen.fill(WHITE)
                            draw_board(self.board, self.screen)
                            self.draw_status()
                            pygame.display.flip()
                            self.update_all_clients()
                    except ValueError:
                        print("Invalid move received")
                        
                else:
                    client_socket.send(f"wait:{self.current_player}".encode('utf-8'))
                    time.sleep(0.5)
                    
        except ConnectionResetError:
            print(f"Player {player_id} disconnected")
            self.remove_client(player_id)
        except Exception as e:
            print(f"Error with player {player_id}: {e}")
            self.remove_client(player_id)

    
    def process_move(self, col, player_id):
        with self.lock:
            if not is_valid_location(self.board, col):
                return False
                
            row = get_next_open_row(self.board, col)
            drop_piece(self.board, row, col, player_id)
            
            # self.screen.fill(WHITE)
            draw_board(self.board, self.screen)
            
            if winning_move(self.board, player_id):
                self.game_over = True
                self.draw_text(f"Player {player_id} wins!", RED, WIDTH // 2 - 100, 10)
                print("Player {player_id} wins!")
                self.notify_all(f"win:{player_id}")
                return True
                
            self.current_player = 2 if self.current_player == 1 else 1
            return True

    def update_all_clients(self):
        board_state = f"board:{self.board.tolist()}:{self.current_player}"
        for client in self.clients:
            try:
                client['socket'].send(board_state.encode('utf-8'))
            except:
                self.remove_client(client['player_id'])

    def notify_all(self, message):
        for client in self.clients[:]:
            try:
                client['socket'].send(message.encode('utf-8'))
            except:
                self.remove_client(client['player_id'])

    def remove_client(self, player_id):
        with self.lock:
            for i, client in enumerate(self.clients[:]):
                if client['player_id'] == player_id:
                    try:
                        client['socket'].close()
                    except:
                        pass
                    self.clients.pop(i)
                    break
            
            if len(self.clients) < 2 and not self.game_over:
                self.game_over = True
                self.notify_all("opponent_disconnected")
                self.draw_text("Player disconnected", RED, WIDTH // 2 - 100, 400)

    def cleanup(self):
        self.game_over = True
        for client in self.clients[:]:
            try:
                client['socket'].send("server_shutdown".encode('utf-8'))
                client['socket'].close()
            except:
                pass
        self.clients = []

def init_server(screen):
    server = Connect4Server(screen)
    server.run()

def exit_online():
    pass