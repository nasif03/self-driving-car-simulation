import pygame

def blit_rotate_center(surf, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = top_left).center)
    surf.blit(rotated_image, new_rect.topleft)