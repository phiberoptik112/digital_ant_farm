import pygame
import math
from typing import Tuple, Callable, Any, Optional

class UISlider:
    """A slider UI component for controlling numeric values."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_val: float, max_val: float, initial_val: float, 
                 label: str, callback: Callable[[float], None] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.callback = callback
        self.dragging = False
        self.knob_pos = self._value_to_pos(initial_val)
        
        # Colors
        self.bg_color = (60, 60, 60)
        self.track_color = (100, 100, 100)
        self.knob_color = (200, 200, 200)
        self.knob_hover_color = (220, 220, 220)
        self.text_color = (255, 255, 255)
        
        # Font
        self.font = pygame.font.Font(None, 20)
        
    def _value_to_pos(self, value: float) -> int:
        """Convert a value to knob position."""
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + ratio * self.rect.width)
    
    def _pos_to_value(self, pos: int) -> float:
        """Convert knob position to value."""
        ratio = (pos - self.rect.x) / self.rect.width
        ratio = max(0, min(1, ratio))  # Clamp to 0-1
        return self.min_val + ratio * (self.max_val - self.min_val)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if event was handled."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                knob_rect = pygame.Rect(self.knob_pos - 8, self.rect.y - 2, 16, self.rect.height + 4)
                if knob_rect.collidepoint(mouse_pos):
                    self.dragging = True
                    return True
                elif self.rect.collidepoint(mouse_pos):
                    # Click on track - move knob to position
                    self.knob_pos = mouse_pos[0]
                    self.val = self._pos_to_value(self.knob_pos)
                    if self.callback:
                        self.callback(self.val)
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.knob_pos = event.pos[0]
                self.knob_pos = max(self.rect.x, min(self.rect.x + self.rect.width, self.knob_pos))
                self.val = self._pos_to_value(self.knob_pos)
                if self.callback:
                    self.callback(self.val)
                return True
        
        return False
    
    def set_value(self, value: float):
        """Set the slider value programmatically."""
        self.val = max(self.min_val, min(self.max_val, value))
        self.knob_pos = self._value_to_pos(self.val)
    
    def draw(self, screen: pygame.Surface):
        """Draw the slider."""
        # Draw track
        pygame.draw.rect(screen, self.track_color, self.rect)
        
        # Draw knob
        mouse_pos = pygame.mouse.get_pos()
        knob_rect = pygame.Rect(self.knob_pos - 8, self.rect.y - 2, 16, self.rect.height + 4)
        knob_color = self.knob_hover_color if knob_rect.collidepoint(mouse_pos) else self.knob_color
        pygame.draw.rect(screen, knob_color, knob_rect)
        
        # Draw label and value
        label_text = self.font.render(f"{self.label}: {self.val:.1f}", True, self.text_color)
        screen.blit(label_text, (self.rect.x, self.rect.y - 25))


class UIButton:
    """A button UI component."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 label: str, callback: Callable[[], None] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.callback = callback
        self.pressed = False
        
        # Colors
        self.bg_color = (80, 80, 80)
        self.hover_color = (100, 100, 100)
        self.press_color = (60, 60, 60)
        self.text_color = (255, 255, 255)
        
        # Font
        self.font = pygame.font.Font(None, 24)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if event was handled."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                if self.rect.collidepoint(mouse_pos):
                    self.pressed = True
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.pressed:
                    self.pressed = False
                    mouse_pos = pygame.mouse.get_pos()
                    if self.rect.collidepoint(mouse_pos):
                        if self.callback:
                            self.callback()
                        return True
        
        return False
    
    def draw(self, screen: pygame.Surface):
        """Draw the button."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Determine button color
        if self.pressed:
            color = self.press_color
        elif self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        else:
            color = self.bg_color
        
        # Draw button
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (150, 150, 150), self.rect, 2)
        
        # Draw label
        text_surf = self.font.render(self.label, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class UICheckbox:
    """A checkbox UI component."""
    
    def __init__(self, x: int, y: int, label: str, initial_value: bool = False,
                 callback: Callable[[bool], None] = None):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.label = label
        self.checked = initial_value
        self.callback = callback
        
        # Colors
        self.bg_color = (80, 80, 80)
        self.check_color = (0, 255, 0)
        self.text_color = (255, 255, 255)
        
        # Font
        self.font = pygame.font.Font(None, 20)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if event was handled."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                # Check both checkbox and label area
                label_surf = self.font.render(self.label, True, self.text_color)
                full_rect = pygame.Rect(self.rect.x, self.rect.y, 
                                      self.rect.width + 10 + label_surf.get_width(), 
                                      self.rect.height)
                
                if full_rect.collidepoint(mouse_pos):
                    self.checked = not self.checked
                    if self.callback:
                        self.callback(self.checked)
                    return True
        
        return False
    
    def set_value(self, value: bool):
        """Set the checkbox value programmatically."""
        self.checked = value
    
    def draw(self, screen: pygame.Surface):
        """Draw the checkbox."""
        # Draw checkbox
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, (150, 150, 150), self.rect, 2)
        
        # Draw checkmark if checked
        if self.checked:
            pygame.draw.line(screen, self.check_color, 
                           (self.rect.x + 4, self.rect.y + 10), 
                           (self.rect.x + 8, self.rect.y + 14), 3)
            pygame.draw.line(screen, self.check_color, 
                           (self.rect.x + 8, self.rect.y + 14), 
                           (self.rect.x + 16, self.rect.y + 6), 3)
        
        # Draw label
        label_surf = self.font.render(self.label, True, self.text_color)
        screen.blit(label_surf, (self.rect.x + 30, self.rect.y + 2))


class FoodSystemUI:
    """UI panel for controlling food system parameters."""
    
    def __init__(self, x: int, y: int, food_manager):
        self.x = x
        self.y = y
        self.food_manager = food_manager
        self.visible = True
        
        # Create UI components
        self.components = []
        
        # Panel background
        self.panel_rect = pygame.Rect(x - 10, y - 10, 280, 400)
        
        # Title
        self.title_font = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 20)
        
        # Sliders
        slider_width = 200
        slider_height = 20
        current_y = y + 30
        
        # Number of food sources
        self.num_sources_slider = UISlider(
            x, current_y, slider_width, slider_height,
            1, 20, food_manager.num_food_sources,
            "Food Sources",
            lambda val: setattr(food_manager, 'num_food_sources', int(val))
        )
        self.components.append(self.num_sources_slider)
        current_y += 50
        
        # Food amount range
        self.min_amount_slider = UISlider(
            x, current_y, slider_width, slider_height,
            10, 200, food_manager.min_food_amount,
            "Min Amount",
            lambda val: setattr(food_manager, 'min_food_amount', val)
        )
        self.components.append(self.min_amount_slider)
        current_y += 50
        
        self.max_amount_slider = UISlider(
            x, current_y, slider_width, slider_height,
            50, 300, food_manager.max_food_amount,
            "Max Amount",
            lambda val: setattr(food_manager, 'max_food_amount', val)
        )
        self.components.append(self.max_amount_slider)
        current_y += 50
        
        # Expiration time
        self.expiration_time_slider = UISlider(
            x, current_y, slider_width, slider_height,
            5, 120, food_manager.expiration_time,
            "Expiration Time (s)",
            lambda val: setattr(food_manager, 'expiration_time', val)
        )
        self.components.append(self.expiration_time_slider)
        current_y += 50
        
        # Refresh time
        self.refresh_time_slider = UISlider(
            x, current_y, slider_width, slider_height,
            10, 180, food_manager.refresh_time,
            "Refresh Time (s)",
            lambda val: setattr(food_manager, 'refresh_time', val)
        )
        self.components.append(self.refresh_time_slider)
        current_y += 50
        
        # Expiration rate
        self.expiration_rate_slider = UISlider(
            x, current_y, slider_width, slider_height,
            0.1, 10, food_manager.expiration_rate,
            "Expiration Rate",
            lambda val: setattr(food_manager, 'expiration_rate', val)
        )
        self.components.append(self.expiration_rate_slider)
        current_y += 50
        
        # Auto-generate checkbox
        self.auto_generate_checkbox = UICheckbox(
            x, current_y, "Auto Generate", food_manager.auto_generate,
            lambda val: setattr(food_manager, 'auto_generate', val)
        )
        self.components.append(self.auto_generate_checkbox)
        current_y += 40
        
        # Buttons
        button_width = 120
        button_height = 30
        
        self.regenerate_button = UIButton(
            x, current_y, button_width, button_height,
            "Regenerate Food",
            lambda: food_manager.regenerate_food()
        )
        self.components.append(self.regenerate_button)
        
        self.clear_button = UIButton(
            x + button_width + 10, current_y, button_width, button_height,
            "Clear All Food",
            lambda: food_manager.clear_all_food()
        )
        self.components.append(self.clear_button)
        
        # Statistics display area
        self.stats_y = current_y + 50
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if event was handled."""
        if not self.visible:
            return False
        
        # Check if event is within panel bounds
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if not self.panel_rect.collidepoint(mouse_pos):
                return False
        
        # Handle events for all components
        for component in self.components:
            if component.handle_event(event):
                return True
        
        return False
    
    def toggle_visibility(self):
        """Toggle the visibility of the UI panel."""
        self.visible = not self.visible
    
    def draw(self, screen: pygame.Surface):
        """Draw the UI panel."""
        if not self.visible:
            return
        
        # Draw panel background
        pygame.draw.rect(screen, (40, 40, 40), self.panel_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.panel_rect, 2)
        
        # Draw title
        title_text = self.title_font.render("Food System Controls", True, (255, 255, 255))
        screen.blit(title_text, (self.x, self.y))
        
        # Draw all components
        for component in self.components:
            component.draw(screen)
        
        # Draw statistics
        stats = self.food_manager.get_statistics()
        stats_text = [
            f"Total Sources: {stats['total_sources']}",
            f"Available: {stats['available_sources']}",
            f"Depleted: {stats['depleted_sources']}",
            f"Expired: {stats['expired_sources']}",
            f"Total Food: {stats['total_food']:.1f}",
            f"Utilization: {stats['utilization_percentage']:.1f}%"
        ]
        
        for i, text in enumerate(stats_text):
            text_surf = self.font.render(text, True, (200, 200, 200))
            screen.blit(text_surf, (self.x, self.stats_y + i * 20))
    
    def update(self):
        """Update the UI (called each frame)."""
        # Sync slider values with food manager in case they were changed elsewhere
        self.num_sources_slider.set_value(self.food_manager.num_food_sources)
        self.min_amount_slider.set_value(self.food_manager.min_food_amount)
        self.max_amount_slider.set_value(self.food_manager.max_food_amount)
        self.expiration_time_slider.set_value(self.food_manager.expiration_time)
        self.refresh_time_slider.set_value(self.food_manager.refresh_time)
        self.expiration_rate_slider.set_value(self.food_manager.expiration_rate)
        self.auto_generate_checkbox.set_value(self.food_manager.auto_generate)