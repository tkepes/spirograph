from Draw import Draw
from Spirograph import Spirograph, pi
import pygame as pg
import pygame_widgets
from pygame.locals import *
from Colours import get_colour
from Parameters import *


def main():
    pg.init()
    pg.font.init()
    # global base_curve_coeffs, curls_curve_coeffs, radius_curve_coeffs
    spiro = Spirograph(width=WIDTH, height=HEIGHT, ADAPTIVE_RATE=ADAPTIVE_RATE, outer_params=outer_params,
                       base_curve=base_curve_coeffs, curls=curls_curve_coeffs, rad_curve=radius_curve_coeffs,
                       rad_f=rad_f, base_f=(base_x, base_y), curls_f=(curls_x, curls_y),
                       ORTHOGONAL_WAVES=ORTHOGONAL_WAVES, NORMALISE_WAVES=NORMALISE_WAVES)
    draw = Draw(width=WIDTH, height=HEIGHT, DISPLAY=True, SAVE_IMAGE=True, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH,
                name=get_name(spiro.R0))
    # DYNAMIC_SHADING=True, MY_COLOUR_SCHEME=True, BIPOLAR_COLOUR_SCHEME=False,
    x, y = spiro.update()
    global POINTS, COLOURS
    POINTS += [(x, y)]
    clock = pg.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False
            elif event.type == WINDOWRESIZED:
                draw.resized()
            elif event.type == VIDEORESIZE:
                # draw.screen.blit(pg.transform.scale(pic, event.dict['size']), (0, 0))
                i = 1
                draw.screen.fill(BACKGROUND)
                while i < len(POINTS):
                    pg.draw.line(draw.screen, COLOURS[i - 1], POINTS[i - 1], POINTS[i], width=LINE_WIDTH)
                    i += 1
                pg.display.update()
                pass
            elif event.type == VIDEOEXPOSE:  # handles window minimising/maximising
                draw.screen.fill(BACKGROUND)
                # screen.fill((0, 0, 0))
                # screen.blit(pygame.transform.scale(pic, screen.get_size()), (0, 0))
                # pygame.display.update()
                pg.display.update()
                pass

        x0, y0 = x, y
        x, y = spiro.update()
        POINTS += [(x, y)]
        colour = get_colour(spiro, colouring_scheme_type=COLOURING_SCHEME_BASE, my_colour_scheme=MY_COLOUR_SCHEME,
                            bipolar_colour_scheme=BIPOLAR_COLOUR_SCHEME, dynamic_shading=DYNAMIC_SHADING)
        COLOURS += [colour]
        draw.draw_window(x0, y0, x, y, colour=colour)
        pygame_widgets.update(events)
        run = spiro.t < 2 * spiro.per * pi
    pg.quit()
    draw.save(name=get_name(spiro.R0), final_save=True)


if __name__ == '__main__':
    main()
