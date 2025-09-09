import pygame
import os
import sys

def test_pygame():
    print("Python version:", sys.version)
    print("Testing pygame installation...")
    
    # Set video driver
    os.environ['SDL_VIDEODRIVER'] = 'cocoa'
    print("Using video driver:", os.environ.get('SDL_VIDEODRIVER'))
    
    # Initialize pygame
    try:
        pygame.init()
        print("Pygame initialized")
        print("Pygame version:", pygame.version.ver)
        print("SDL version:", pygame.get_sdl_version())
        
        # Try to create a window
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("Pygame Test")
        print("Window created successfully")
        
        # Fill screen with white
        screen.fill((255, 255, 255))
        pygame.display.flip()
        print("Screen updated")
        
        # Wait for 3 seconds
        pygame.time.wait(3000)
        print("Test completed successfully")
        
    except Exception as e:
        print("Error:", str(e))
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == "__main__":
    test_pygame()
