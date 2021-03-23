import pygame
import pygame_gui
from pygame_gui.core.interfaces import container_interface

pygame.init()

pygame.display.set_caption("Quick Start")
window_surface = pygame.display.set_mode((800, 600))

background = pygame.Surface((800, 600))
background.fill(pygame.Color("#000000"))

manager = pygame_gui.UIManager((800, 600))

top_panel = pygame_gui.elements.UIPanel(
    starting_layer_height=0, manager=manager, relative_rect=pygame.Rect(0, 0, 800, 50)
)

altitude_text = pygame_gui.elements.ui_text_box.UITextBox(
    manager=manager,
    container=top_panel,
    html_text="Altitude",
    relative_rect=pygame.Rect(10, 5, 80, 35),
    visible=True,
)

altitude_textentry = pygame_gui.elements.UITextEntryLine(
    manager=manager,
    container=top_panel,
    relative_rect=pygame.Rect(100, 10, 50, 40),
    visible=True,
)
altitude_textentry.set_text_length_limit(4)
altitude_textentry.set_allowed_characters("numbers")

heading_text = pygame_gui.elements.ui_text_box.UITextBox(
    manager=manager,
    container=top_panel,
    html_text="Heading",
    relative_rect=pygame.Rect(160, 5, 80, 35),
    visible=True,
)

heading_textentry = pygame_gui.elements.UITextEntryLine(
    manager=manager,
    container=top_panel,
    relative_rect=pygame.Rect(250, 10, 40, 40),
    visible=True,
)
heading_textentry.set_text_length_limit(3)
heading_textentry.set_allowed_characters("numbers")

speed_text = pygame_gui.elements.ui_text_box.UITextBox(
    manager=manager,
    container=top_panel,
    html_text="Speed",
    relative_rect=pygame.Rect(300, 5, 80, 35),
    visible=True,
)

speed_textentry = pygame_gui.elements.UITextEntryLine(
    manager=manager,
    container=top_panel,
    relative_rect=pygame.Rect(390, 10, 40, 40),
    visible=True,
)
speed_textentry.set_text_length_limit(3)
speed_textentry.set_allowed_characters("numbers")

name_text = pygame_gui.elements.ui_text_box.UITextBox(
    manager=manager,
    container=top_panel,
    html_text="Name",
    relative_rect=pygame.Rect(470, 5, 80, 35),
    visible=True,
)

name_textentry = pygame_gui.elements.UITextEntryLine(
    manager=manager,
    container=top_panel,
    relative_rect=pygame.Rect(560, 10, 70, 40),
    visible=True,
)
name_textentry.set_text_length_limit(7)

submit_button = pygame_gui.elements.ui_button.UIButton(
    manager=manager,
    container=top_panel,
    text="Submit",
    relative_rect=pygame.Rect(660, 5, 70, 35),
    visible=True,
)

clock = pygame.time.Clock()
is_running = True

while is_running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                manager.set_visual_debug_mode(True)
            if event.key == pygame.K_F2:
                manager.set_visual_debug_mode(False)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == submit_button:
                    try:
                        if int(heading_textentry.get_text()) > 360:
                            print("Why did you do that?")
                    except ValueError:
                        pass
                    print(
                        f"We want a plane named {name_textentry.get_text()}\n"
                        f"At altitude {altitude_textentry.get_text()}\n"
                        f"Going at a heading of "
                        f"{heading_textentry.get_text()}\n"
                        f"Crusing at {speed_textentry.get_text()}"
                    )
        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()
