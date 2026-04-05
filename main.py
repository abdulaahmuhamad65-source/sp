import pygame
import random
import math

# 1. الإعدادات
pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
font = pygame.font.SysFont("monospace", 40, bold=True)
clock = pygame.time.Clock()

# --- كائنات الفضاء ---
stars = [[random.randint(0, W), random.randint(0, H), random.uniform(1, 4)] for _ in range(80)]
particles = [] 

def play_sound(freq, duration=0.1):
    try:
        n_samples = int(44100 * duration)
        buf = bytearray()
        for i in range(n_samples):
            t = i / 44100
            value = int(127 * math.sin(2.0 * math.pi * freq * t))
            buf.append(value + 128)
        pygame.mixer.Sound(buffer=buf).play()
    except: pass

def create_particles(x, y, color):
    for _ in range(15):
        particles.append([[x, y], [random.uniform(-4, 4), random.uniform(-4, 4)], random.randint(4, 8), color])

# --- متغيرات اللعبة (تعديل مكان اللاعب ليكون ظاهراً) ---
# رفعنا اللاعب ليكون على ارتفاع 250 بكسل من القاع بدلاً من 180
player_rect = pygame.Rect(W//2 - 45, H - 250, 90, 90)
bullets, enemies, powerups, bombs = [], [], [], []
score, lives = 0, 3
game_over, is_super, super_ticks, shake = False, False, 0, 0

running = True
while running:
    clock.tick(60)
    mx, my = pygame.mouse.get_pos()
    
    ox, oy = (random.randint(-shake, shake), random.randint(-shake, shake)) if shake > 0 else (0, 0)
    if shake > 0: shake -= 1

    screen.fill((5, 5, 15)) 

    for s in stars:
        s[1] += s[2] 
        if s[1] > H: s[1], s[0] = 0, random.randint(0, W)
        pygame.draw.circle(screen, (200, 200, 255), (int(s[0]+ox), int(s[1]+oy)), 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not game_over:
                bomb_hit = False
                for b_item in bombs[:]:
                    if b_item.collidepoint((mx, my)):
                        for e in enemies: create_particles(e.centerx, e.centery, (255, 50, 50))
                        enemies, score, shake, bomb_hit = [], score + 5, 30, True
                        bombs.remove(b_item); play_sound(80, 0.6); break
                
                if not bomb_hit:
                    # الطلقة تخرج من فوهة المدفع
                    bullets.append(pygame.Rect(player_rect.centerx - 5, player_rect.top - 10, 10, 30))
                    if is_super:
                        bullets.append(pygame.Rect(player_rect.left, player_rect.top+10, 10, 30))
                        bullets.append(pygame.Rect(player_rect.right-10, player_rect.top+10, 10, 30))
                    play_sound(1500 if not is_super else 2500)
            else:
                if W//2-150 < mx < W//2+150:
                    if H//2 < my < H//2+80: 
                        score, lives, game_over, is_super, shake, enemies, bullets, powerups, bombs, particles = 0, 3, False, False, 0, [], [], [], [], []
                    if H//2+100 < my < H//2+180: running = False

    if not game_over:
        player_rect.centerx = mx
        if is_super and (pygame.time.get_ticks() - super_ticks) > 12000: is_super = False

        for b in bullets[:]:
            b.y -= 22
            if b.bottom < 0: bullets.remove(b)

        if random.randint(1, max(15, 40-(score//10))) == 1:
            enemies.append(pygame.Rect(random.randint(50, W-100), -50, 75, 75))
        
        if random.randint(1, 1000) == 1: bombs.append(pygame.Rect(random.randint(100, W-100), random.randint(100, H-400), 75, 75))

        for e in enemies[:]:
            e.y += 4 + (score * 0.1)
            for b in bullets[:]:
                if e.colliderect(b):
                    create_particles(e.centerx, e.centery, (255, 100, 100))
                    if e in enemies: enemies.remove(e)
                    if b in bullets: bullets.remove(b)
                    score += 1; shake = 5
                    if score % 10 == 0: powerups.append(pygame.Rect(e.x, e.y, 60, 60))
                    break
            if e.colliderect(player_rect):
                lives -= 1; enemies.remove(e); shake = 20; play_sound(400, 0.3)
                if lives <= 0: game_over = True
            elif e.top > H: enemies.remove(e)

        for p_up in powerups[:]:
            p_up.y += 6 
            pygame.draw.circle(screen, (0, 255, 100), (p_up.centerx+ox, p_up.centery+oy), 30)
            if p_up.colliderect(player_rect):
                is_super, super_ticks = True, pygame.time.get_ticks()
                powerups.remove(p_up); play_sound(3000, 0.3)
            elif p_up.top > H: powerups.remove(p_up)

        # تحريك الشرارات
        for p in particles[:]:
            p[0][0] += p[1][0]; p[0][1] += p[1][1]; p[2] -= 0.2
            if p[2] <= 0: particles.remove(p)
            else: pygame.draw.circle(screen, p[3], (int(p[0][0]+ox), int(p[0][1]+oy)), int(p[2]))

    # --- الرسم ---
    if not game_over:
        p_color = (255, 255, 0) if is_super else (0, 255, 255)
        # رسم جسم اللاعب
        pygame.draw.rect(screen, p_color, (player_rect.x+ox, player_rect.y+oy, 90, 90), border_radius=15)
        # رسم "فوهة المدفع" لتمييز شكل اللاعب
        pygame.draw.rect(screen, p_color, (player_rect.centerx-15+ox, player_rect.top-20+oy, 30, 30), border_radius=5)
        
        for b in bullets: pygame.draw.rect(screen, (255, 255, 0), (b.x+ox, b.y+oy, 10, 30))
        for e in enemies: pygame.draw.rect(screen, (255, 50, 50), (e.x+ox, e.y+oy, 75, 75), border_radius=15)
        for b_b in bombs: 
            b_c = (255, 0, 0) if (pygame.time.get_ticks()//150)%2==0 else (50, 0, 0)
            pygame.draw.circle(screen, b_c, (b_b.centerx+ox, b_b.centery+oy), 35)

    screen.blit(font.render(f"SCORE: {score}", 1, (255, 255, 255)), (50+ox, 50+oy))
    for i in range(lives): pygame.draw.rect(screen, (255, 0, 0), (50+(i*55)+ox, 110+oy, 45, 45), border_radius=8)
    
    if game_over:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0,0))
        pygame.draw.rect(screen, (0, 200, 0), (W//2-150, H//2, 300, 80), border_radius=15)
        screen.blit(font.render("RESTART", 1, (255,255,255)), (W//2-80, H//2+20))
        pygame.draw.rect(screen, (200, 0, 0), (W//2-150, H//2+100, 300, 80), border_radius=15)
        screen.blit(font.render("EXIT", 1, (255,255,255)), (W//2-50, H//2+120))

    pygame.display.flip()
pygame.quit()