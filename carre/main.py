import pygame
from menu import main_menu 
def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("60 Seconds!")
    main_menu(screen) 

if __name__ == "__main__":
    main()
