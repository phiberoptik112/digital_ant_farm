import pygame
from typing import Dict, Optional, Callable
from entities.ant import AntCaste
from entities.colony import Colony

class QueenControls:
    """
    UI component for queen controls to produce different ant castes.
    """
    
    def __init__(self, x: int, y: int, width: int = 250, height: int = 300):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # UI elements
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Define ant castes with their properties
        self.ant_castes = {
            AntCaste.WORKER: {
                'name': 'Worker',
                'color': (255, 255, 0),
                'cost': 10.0,
                'description': 'Balanced foragers'
            },
            AntCaste.SOLDIER: {
                'name': 'Soldier',
                'color': (255, 0, 0),
                'cost': 15.0,
                'description': 'Strong defenders'
            },
            AntCaste.SCOUT: {
                'name': 'Scout',
                'color': (0, 255, 0),
                'cost': 12.0,
                'description': 'Fast explorers'
            },
            AntCaste.NURSE: {
                'name': 'Nurse',
                'color': (255, 192, 203),
                'cost': 8.0,
                'description': 'Colony maintainers'
            }
        }
        
        # Input fields for each caste
        self.input_fields = {}
        self.input_values = {}
        self.active_input = None
        
        # Initialize input fields
        for caste in self.ant_castes.keys():
            self.input_fields[caste] = {
                'rect': pygame.Rect(0, 0, 60, 25),
                'active': False
            }
            self.input_values[caste] = '1'
        
        # Buttons for each caste
        self.buttons = {}
        self._setup_ui_elements()
        
    def _setup_ui_elements(self):
        """Set up the positions of UI elements."""
        y_offset = 40
        button_height = 35
        spacing = 5
        
        for i, caste in enumerate(self.ant_castes.keys()):
            y_pos = self.y + y_offset + i * (button_height + spacing)
            
            # Button rectangle
            button_rect = pygame.Rect(self.x + 10, y_pos, 120, button_height)
            self.buttons[caste] = button_rect
            
            # Input field rectangle
            input_rect = pygame.Rect(self.x + 140, y_pos + 5, 60, 25)
            self.input_fields[caste]['rect'] = input_rect
    
    def handle_event(self, event: pygame.event.Event, colony: Colony) -> bool:
        """
        Handle pygame events for the queen controls.
        Returns True if the event was handled, False otherwise.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check button clicks
            for caste, button_rect in self.buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    self._produce_ants(caste, colony)
                    return True
            
            # Check input field clicks
            for caste, field_data in self.input_fields.items():
                if field_data['rect'].collidepoint(mouse_pos):
                    # Deactivate all other fields
                    for other_caste in self.input_fields:
                        self.input_fields[other_caste]['active'] = False
                    # Activate clicked field
                    field_data['active'] = True
                    self.active_input = caste
                    return True
            
            # Click outside any input field - deactivate all
            for caste in self.input_fields:
                self.input_fields[caste]['active'] = False
            self.active_input = None
            
        elif event.type == pygame.KEYDOWN:
            if self.active_input is not None:
                if event.key == pygame.K_RETURN:
                    # Enter key - produce ants
                    self._produce_ants(self.active_input, colony)
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    # Backspace - remove last character
                    if self.input_values[self.active_input]:
                        self.input_values[self.active_input] = self.input_values[self.active_input][:-1]
                    return True
                elif event.unicode.isdigit():
                    # Number input - add to current value
                    current_value = self.input_values[self.active_input]
                    if len(current_value) < 3:  # Limit to 3 digits
                        self.input_values[self.active_input] = current_value + event.unicode
                    return True
        
        return False
    
    def _produce_ants(self, caste: AntCaste, colony: Colony):
        """Produce ants of the specified caste."""
        try:
            count = int(self.input_values[caste]) if self.input_values[caste] else 1
            count = max(1, min(count, 50))  # Limit between 1 and 50
            
            if colony.can_spawn_caste(caste, count):
                spawned_ants = colony.spawn_multiple_ants(caste, count)
                print(f"Spawned {len(spawned_ants)} {self.ant_castes[caste]['name']} ants")
            else:
                print(f"Cannot spawn {count} {self.ant_castes[caste]['name']} ants - insufficient resources or space")
                
        except ValueError:
            print(f"Invalid number input for {self.ant_castes[caste]['name']}")
    
    def draw(self, screen: pygame.Surface, colony: Colony):
        """Draw the queen controls UI."""
        # Draw background panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (40, 40, 40), panel_rect)
        pygame.draw.rect(screen, (100, 100, 100), panel_rect, 2)
        
        # Draw title
        title_text = self.font.render("Queen Controls", True, (255, 255, 255))
        screen.blit(title_text, (self.x + 10, self.y + 10))
        
        # Draw controls for each caste
        for caste, caste_info in self.ant_castes.items():
            self._draw_caste_control(screen, caste, caste_info, colony)
        
        # Draw colony info
        self._draw_colony_info(screen, colony)
    
    def _draw_caste_control(self, screen: pygame.Surface, caste: AntCaste, caste_info: Dict, colony: Colony):
        """Draw controls for a specific ant caste."""
        button_rect = self.buttons[caste]
        input_rect = self.input_fields[caste]['rect']
        
        # Check if we can spawn this caste
        try:
            count = int(self.input_values[caste]) if self.input_values[caste] else 1
            can_spawn = colony.can_spawn_caste(caste, count)
        except ValueError:
            can_spawn = False
        
        # Draw button
        button_color = (60, 120, 60) if can_spawn else (120, 60, 60)
        pygame.draw.rect(screen, button_color, button_rect)
        pygame.draw.rect(screen, (150, 150, 150), button_rect, 2)
        
        # Button text
        button_text = f"Produce {caste_info['name']}"
        text_surface = self.small_font.render(button_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)
        
        # Draw input field
        input_active = self.input_fields[caste]['active']
        input_color = (80, 80, 80) if input_active else (60, 60, 60)
        border_color = (200, 200, 200) if input_active else (100, 100, 100)
        
        pygame.draw.rect(screen, input_color, input_rect)
        pygame.draw.rect(screen, border_color, input_rect, 2)
        
        # Input text
        input_text = self.input_values[caste] if self.input_values[caste] else '1'
        text_surface = self.small_font.render(input_text, True, (255, 255, 255))
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 3))
        
        # Draw cost and population info
        cost_text = f"Cost: {caste_info['cost']}"
        population = colony.get_caste_population(caste)
        pop_text = f"Population: {population}"
        
        cost_surface = self.small_font.render(cost_text, True, (200, 200, 200))
        pop_surface = self.small_font.render(pop_text, True, caste_info['color'])
        
        screen.blit(cost_surface, (self.x + 210, button_rect.y))
        screen.blit(pop_surface, (self.x + 210, button_rect.y + 12))
    
    def _draw_colony_info(self, screen: pygame.Surface, colony: Colony):
        """Draw general colony information."""
        info_y = self.y + self.height - 60
        
        # Draw separator line
        pygame.draw.line(screen, (100, 100, 100), 
                        (self.x + 10, info_y - 10), 
                        (self.x + self.width - 10, info_y - 10), 2)
        
        # Colony stats
        stats = colony.get_statistics()
        info_lines = [
            f"Food: {stats['food_storage']:.1f}/{stats['max_food_storage']:.1f}",
            f"Total Pop: {stats['population']}/{stats['max_population']}",
            f"Level: {stats['development_level']}"
        ]
        
        for i, line in enumerate(info_lines):
            text_surface = self.small_font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (self.x + 10, info_y + i * 15))