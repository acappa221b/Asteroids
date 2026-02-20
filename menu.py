import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT_SIZE, UI_SMALL_FONT_SIZE, UI_PADDING
from highscores import HighscoreManager

class MenuScreen:
    """Main menu with ASCII art spaceship"""
    
    SPACESHIP_ASCII = [
        """                                       _,'/
                                  _.-''._:
                          ,-:`-.-'    .:.|
                         ;-.''       .::.|
          _..------.._  / (:.       .:::.|
       ,'.   .. . .  .`/  : :.     .::::.|
     ,'. .    .  .   ./    \ ::. .::::::.|
   ,'. .  .    .   . /      `.,,::::::::.;\
  /  .            . /       ,',';_::::::,:_:
 / . .  .   .      /      ,',','::`--'':;._;
: .             . /     ,',',':::::::_:'_,'
|..  .   .   .   /    ,',','::::::_:'_,'
|.              /,-. /,',':::::_:'_,'
| ..    .    . /) /-:/,'::::_:',-'
: . .     .   // / ,'):::_:',' ;
 \ .   .     // /,' /,-.','  ./
  \ . .  `::./,// ,'' ,'   . /
   `. .   . `;;;,/_.'' . . ,'
    ,`. .   :;;' `:.  .  ,'
   /   `-._,'  ..  ` _.-'
  (     _,'``------''  SSt
   `--''
        
        """]
    
    def __init__(self):
        self.selected_option = 0  # 0: New Game, 1: Debug Mode, 2: Highscores, 3: Exit
        self.options = ["NEW GAME", "DEBUG MODE", "HIGHSCORES", "EXIT"]
        self.highscore_manager = HighscoreManager()
        self.show_highscores = False
        self.fonts = {}
        self.button_rects = []  # Store button positions for mouse click detection
    
    def setup_fonts(self):
        """Setup pygame fonts"""
        self.fonts['title'] = pygame.font.Font(None, 64)
        self.fonts['large'] = pygame.font.Font(None, UI_FONT_SIZE)
        self.fonts['normal'] = pygame.font.Font(None, UI_SMALL_FONT_SIZE)
        self.fonts['small'] = pygame.font.Font(None, 20)
        self.fonts['mono'] = pygame.font.Font(None, 18)  # For highscores
    
    def handle_input(self, event):
        """Handle menu input, returns action"""
        if event.type == pygame.KEYDOWN:
            if self.show_highscores:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    self.show_highscores = False
                    return None
            else:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return self._get_action_for_option(self.selected_option)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle mouse clicks on menu buttons
            if not self.show_highscores:
                for i, rect in enumerate(self.button_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_option = i
                        return self._get_action_for_option(i)
        
        return None
    
    def _get_action_for_option(self, option_index):
        """Get the action for a selected option"""
        if option_index == 0:
            return "NEW_GAME"
        elif option_index == 1:
            return "DEBUG_MODE"
        elif option_index == 2:
            self.show_highscores = True
            return None
        elif option_index == 3:
            return "EXIT"
        return None
    
    def draw_spaceship(self, screen):
        """Draw ASCII spaceship"""
        font = self.fonts['small']
        
        # Calculate starting position to center horizontally
        ship_width = max(len(line) for line in self.SPACESHIP_ASCII)
        char_width = font.size('A')[0]
        start_x = (SCREEN_WIDTH - (ship_width * char_width)) // 2
        start_y = 80
        
        for i, line in enumerate(self.SPACESHIP_ASCII):
            text_surface = font.render(line, True, (0, 255, 0))
            screen.blit(text_surface, (start_x, start_y + i * 18))
    
    def draw_menu(self, screen):
        """Draw main menu"""
        if not self.fonts:
            self.setup_fonts()
        
        screen.fill((10, 10, 20))
        
        # Draw spaceship
        self.draw_spaceship(screen)
        
        # Draw title
        title = self.fonts['title'].render("VOIDFALL", True, (0, 200, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 450))
        screen.blit(title, title_rect)
        
        # Draw menu options
        menu_y = 550
        option_spacing = 60
        self.button_rects = []  # Reset button rects for this frame
        
        for i, option in enumerate(self.options):
            color = (255, 215, 0) if i == self.selected_option else (200, 200, 200)
            
            # Highlight selected option
            if i == self.selected_option:
                # Draw selection box
                option_font = self.fonts['large']
                text = option_font.render(f"> {option} <", True, color)
            else:
                option_font = self.fonts['large']
                text = option_font.render(f"  {option}  ", True, color)
            
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, menu_y + i * option_spacing))
            # Add padding to make buttons easier to click
            button_rect = text_rect.inflate(40, 20)
            self.button_rects.append(button_rect)
            
            # Draw button background/border if selected
            if i == self.selected_option:
                pygame.draw.rect(screen, color, button_rect, 3)
            
            screen.blit(text, text_rect)
        
        # Draw instructions
        instruction = self.fonts['small'].render("USE W/↑ AND S/↓ TO SELECT | CLICK OR ENTER TO CONFIRM", True, (150, 150, 150))
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        screen.blit(instruction, instruction_rect)
    
    def draw_highscores(self, screen):
        """Draw highscores screen"""
        if not self.fonts:
            self.setup_fonts()
        
        screen.fill((10, 10, 20))
        
        # Reload scores from file to get the latest ones
        self.highscore_manager.scores = self.highscore_manager.load_scores()
        
        # Title
        title = self.fonts['title'].render("TOP 10 SCORES", True, (0, 200, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title, title_rect)
        
        # Highscores
        scores_text = self.highscore_manager.get_formatted_scores()
        lines = scores_text.split('\n')
        
        y_pos = 100
        for line in lines:
            text_surface = self.fonts['mono'].render(line, True, (0, 255, 100))
            screen.blit(text_surface, (50, y_pos))
            y_pos += 25
        
        # Instructions
        instruction = self.fonts['small'].render("PRESS ESC OR BACKSPACE TO RETURN", True, (150, 150, 150))
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        screen.blit(instruction, instruction_rect)
    
    def draw(self, screen):
        """Draw current screen"""
        if self.show_highscores:
            self.draw_highscores(screen)
        else:
            self.draw_menu(screen)
