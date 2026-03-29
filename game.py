import pgzrun
import pygame
import random
import time
import math

# =====================================================================
# --- AYARLAR VE RENKLER ---
# =====================================================================
WIDTH = 1440
HEIGHT = 900
TITLE = "GÖKTEN ÖTE"

music.play("abc")
music.set_volume(0.1)


mode = "intro"
MAIN_BLUE = (0, 174, 239)
GLOW_BLUE = (100, 220, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
WHITE = (255, 255, 255)

# =====================================================================
# --- AKTÖRLER VE SAHNELER ---
# =====================================================================
player = Actor("player", (WIDTH // 2, 700))
npc = Actor("npc", (1200, 750))

background = Actor("bg") # Menü
background._surf = pygame.transform.scale(background._surf, (WIDTH, HEIGHT))

bg3 = Actor("bg3", (WIDTH//2, HEIGHT//2)) # NASA Odası

bg4 = Actor("bg4") # Uzay Gemisi
bg4._surf = pygame.transform.scale(bg4._surf, (WIDTH, HEIGHT))
bg4.topleft = (0, 0)

bg5 = Actor("bg5") # Final Sahnesi (Ay'a İniş)
bg5._surf = pygame.transform.scale(bg5._surf, (WIDTH, HEIGHT))
bg5.topleft = (0, 0)

bg6 = Actor("bg6") 
bg6._surf = pygame.transform.scale(bg6._surf, (WIDTH, HEIGHT))
bg6.topleft = (0, 0)

# --- YENİ EKLENEN BG7 ---
bg7 = Actor("bg7") 
try:
    bg7._surf = pygame.transform.scale(bg7._surf, (WIDTH, HEIGHT))
except: pass
bg7.topleft = (0, 0)

# Koordinatlar
pc_egitim_x, pc_egitim_y = 310, 410
pc_gemi_x, pc_gemi_y = 350, 530     
kova_x, kova_y = 1195, 680 
oksijen_x, oksijen_y = 80, 680
jen_panel_x, jen_panel_y = 135, 480 

def resize_player():
    try: player._surf = pygame.transform.scale(player._surf, (npc.width, npc.height))
    except: pass
resize_player()

# =====================================================================
# --- DEĞİŞKENLER ---
# =====================================================================
test_gechildi = False # Yeni kıyafetler için kontrol değişkeni

uzay_bilgileri = [
    "Uzaya gonderilen ilk canlilar maymun ya da kopek degil, 1947 yilinda ABD tarafindan gonderilen meyve sinekleridir.",
    "Uluslararasi Uzay Istasyonu’ndaki astronotlar her 90 dakikada bir yorunge degistirdigi icin gunde 15 kez gun dogumu yasarlar.",
    "Uzayda ses yayilmaz cunku ses dalgalarinin iletilecegi bir ortam yoktur.",
    "Ay’a simdiye kadar yalnizca 12 kisi ayak basabilmistir.",
    "Astronotlara gore uzay; kaynak dumani, sicak metal ve barut kokusuna benzer bir kokuya sahiptir."
]

bilgi_sirasi = 0
guc_bari = 0
g_bari_val = 100
g_baslangic_vakti = 0
last_g_press_time = 0
fade_alfa = 0
fade_baslasin = False
fade_hedef = ""
shake_amount = 0
shake_x, shake_y = 0, 0

# Görev Durumları
atik_tamamlandi = False
o2_tamamlandi = False
jen_tamamlandi = False
rota_tamamlandi = False

# Mini Oyun Verileri
dusman_atiklar = []
mini_oyun_skor = 0
mini_oyun_can = 3
mini_oyun_hedef = 15
o2_basinc = 50 
o2_gorev_vakti = 0
o2_basari_sure = 10 
jen_imlec_x = WIDTH // 2
jen_yon = 1
jen_hiz = 10
jen_basari_sayisi = 0
target_route = [0, 0, 0, 0]
player_route = [0, 0, 0, 0]
active_digit = 0

def yeni_atik_olustur():
    resim = random.choice(["vida", "uydu"])
    try: atik = Actor(resim)
    except: atik = Actor("player")
    atik._surf = pygame.transform.scale(atik._surf, (80, 80))
    atik.x = random.randint(150, WIDTH - 150)
    atik.y = -100
    atik.speed = random.uniform(4, 9)
    atik.rot_speed = random.randint(-5, 5)
    dusman_atiklar.append(atik)

# Intro
intro_baslangic = time.time()
kozmoz_harfler = "KOZMOS"
harf_cisimleri = []
kozmoz_tamamlandi = False
intro_parlama_alfa = 0

def prepare_intro_letters():
    char_spacing = 100
    start_x = (WIDTH // 2) - ((len(kozmoz_harfler)-1) * char_spacing // 2)
    for i, harf in enumerate(kozmoz_harfler):
        harf_cisimleri.append({'char': harf, 'pos': [random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)], 'target_pos': (start_x + i * char_spacing, HEIGHT // 2), 'current_char': random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")})
prepare_intro_letters()

# =====================================================================
# --- UPDATE ---
# =====================================================================
def update():
    global mode, kozmoz_tamamlandi, intro_parlama_alfa, shake_amount, shake_x, shake_y
    global g_bari_val, g_baslangic_vakti, fade_alfa, fade_baslasin, fade_hedef
    global mini_oyun_skor, mini_oyun_can, guc_bari, o2_basinc, o2_gorev_vakti
    global jen_imlec_x, jen_yon, atik_tamamlandi, o2_tamamlandi, jen_tamamlandi

    if shake_amount > 0:
        shake_x = random.randint(-shake_amount, shake_amount); shake_y = random.randint(-shake_amount, shake_amount)
        shake_amount -= 1
    else: shake_x, shake_y = 0, 0

    if fade_baslasin:
        fade_alfa += 5
        if fade_alfa >= 255:
            fade_alfa = 255; fade_baslasin = False; mode = fade_hedef; player.pos = (WIDTH // 2, 700); fade_alfa = 0

    if guc_bari >= 100 and mode == "uzay_gemisi" and not fade_baslasin:
        fade_baslasin = True
        fade_hedef = "final_sahne"

    if mode == "intro":
        tamam = True
        for h in harf_cisimleri:
            h['pos'][0] += (h['target_pos'][0] - h['pos'][0]) * 0.05
            h['pos'][1] += (h['target_pos'][1] - h['pos'][1]) * 0.05
            if not kozmoz_tamamlandi: h['current_char'] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            if abs(h['pos'][0] - h['target_pos'][0]) > 5: tamam = False
        if tamam and not kozmoz_tamamlandi and (time.time() - intro_baslangic) > 1.5:
            kozmoz_tamamlandi = True; intro_parlama_alfa = 255
        if kozmoz_tamamlandi:
            intro_parlama_alfa = max(0, intro_parlama_alfa - 10)
            if intro_parlama_alfa == 0 and (time.time() - intro_baslangic) > 3.5: mode = "menu"

    elif mode in ["oyun", "uzay_gemisi"]:
        eski_resim = player.image
        # KARAKTER DEĞİŞİM MANTIĞI:
        if keyboard.left or keyboard.a: 
            player.x -= 8
            player.image = "astro3" if test_gechildi else "player3"
        if keyboard.right or keyboard.d: 
            player.x += 8
            player.image = "astro4" if test_gechildi else "player2"
        if keyboard.up or keyboard.w: 
            player.y -= 8
            player.image = "astro" if test_gechildi else "player"
        if keyboard.down or keyboard.s: 
            player.y += 8
            player.image = "astro2" if test_gechildi else "player1"
            
        if player.image != eski_resim: resize_player()
        player.x = max(50, min(WIDTH-50, player.x))
        if mode == "oyun": player.y = max(380, min(810, player.y)) 
        else: player.y = max(560, min(840, player.y))

    elif mode == "atik_mini_oyun":
        if random.random() < 0.05: yeni_atik_olustur()
        for atik in dusman_atiklar[:]:
            atik.y += atik.speed
            atik.angle += atik.rot_speed
            if atik.y > HEIGHT + 100:
                dusman_atiklar.remove(atik); mini_oyun_can -= 1
                if mini_oyun_can <= 0: mode = "game_over"
        if mini_oyun_skor >= mini_oyun_hedef:
            guc_bari = min(100, guc_bari + 25) 
            atik_tamamlandi = True; mode = "uzay_gemisi"; dusman_atiklar.clear()

    elif mode == "o2_mini_oyun":
        o2_basinc += 0.7 
        if keyboard.space: o2_basinc -= 1.8
        if o2_basinc <= 0 or o2_basinc >= 100: mode = "game_over"
        if time.time() - o2_gorev_vakti >= o2_basari_sure:
            guc_bari = min(100, guc_bari + 25) 
            o2_tamamlandi = True; mode = "uzay_gemisi"

    elif mode == "jen_mini_oyun":
        jen_imlec_x += jen_hiz * jen_yon
        if jen_imlec_x > WIDTH // 2 + 300 or jen_imlec_x < WIDTH // 2 - 300: jen_yon *= -1

    elif mode == "gorev_gforce":
        shake_amount = 15
        g_bari_val -= 0.85
        if g_bari_val <= 0: mode = "game_over"
        elif time.time() - g_baslangic_vakti >= 15: mode = "gorev_gforce_basari"

# =====================================================================
# --- DRAW ---
# =====================================================================
def draw():
    screen.clear()
    
    if mode == "intro":
        screen.fill("black")
        for h in harf_cisimleri:
            clr = GLOW_BLUE if kozmoz_tamamlandi else (180, 180, 180)
            screen.draw.text(h['current_char'] if not kozmoz_tamamlandi else h['char'], center=(h['pos'][0], h['pos'][1]), fontsize=100, color=clr)
        if intro_parlama_alfa > 0:
            s = pygame.Surface((WIDTH, HEIGHT)); s.set_alpha(intro_parlama_alfa); s.fill(WHITE); screen.blit(s, (0,0))
            
    elif mode == "menu":
        background.draw()
        screen.draw.text("GÖKTEN ÖTE", center=(WIDTH//2, 220), fontsize=120, color=GLOW_BLUE, shadow=(3,3))
        btn_basla = Rect((WIDTH//2 - 150, 420), (300, 70))
        btn_bilgi = Rect((WIDTH//2 - 150, 510), (300, 70))
        btn_cikis = Rect((WIDTH//2 - 150, 600), (300, 70))
        screen.draw.filled_rect(btn_basla, MAIN_BLUE); screen.draw.text("OYUNA BAŞLA", center=btn_basla.center, fontsize=35, color=WHITE)
        screen.draw.filled_rect(btn_bilgi, (100,100,100)); screen.draw.text("BİLGİ", center=btn_bilgi.center, fontsize=35, color=WHITE)
        screen.draw.filled_rect(btn_cikis, RED); screen.draw.text("ÇIKIŞ", center=btn_cikis.center, fontsize=35, color=WHITE)

    elif mode == "bilgi":
        background.draw()
        overlay = pygame.Surface((1000, 600)); overlay.set_alpha(210); overlay.fill((0, 0, 0)); screen.blit(overlay, (WIDTH//2 - 500, 150))
        screen.draw.text("KONTROLLER", center=(WIDTH//2, 200), fontsize=60, color=GLOW_BLUE)
        info = "- W,A,S,D: Hareket\n- SPACE: Etkilesim\n- ENTER: Onayla / Diyalog Gec"
        screen.draw.text(info, (WIDTH//2-450, 320), fontsize=30, color=WHITE)
        btn_geri = Rect((WIDTH//2-100, 700), (200, 50)); screen.draw.filled_rect(btn_geri, MAIN_BLUE); screen.draw.text("GERI", center=btn_geri.center, fontsize=35, color=WHITE)

    elif mode == "oyun":
        bg3.draw()
        npc.pos = (1200 + shake_x, 750 + shake_y); npc.draw()
        player.pos = (player.x + shake_x, player.y + shake_y); player.draw()
        if math.sqrt((player.x - pc_egitim_x)**2 + (player.y - pc_egitim_y)**2) < 180:
            screen.draw.text("BİLGİ ALMAK İÇİN [SPACE]", center=(pc_egitim_x + shake_x, pc_egitim_y - 45 + shake_y), color="cyan", fontsize=20, owidth=1.2, ocolor="black")
        if math.sqrt((player.x - npc.x)**2 + (player.y - npc.y)**2) < 200:
            screen.draw.text("KONUŞMAK İÇİN [SPACE]", center=(npc.x, npc.y - 120), color="yellow", fontsize=45, owidth=1.5, ocolor="black")

    elif mode == "uzay_gemisi":
        bg4.draw()
        player.pos = (player.x + shake_x, player.y + shake_y); player.draw()
        if not rota_tamamlandi and math.sqrt((player.x - pc_gemi_x)**2 + (player.y - pc_gemi_y)**2) < 150:
            screen.draw.text("ROTA OLUŞTUR [SPACE]", center=(pc_gemi_x + 50, pc_gemi_y - 80), color="cyan", fontsize=20, owidth=1, ocolor="black")
        if not o2_tamamlandi and math.sqrt((player.x - oksijen_x)**2 + (player.y - oksijen_y)**2) < 150:
            screen.draw.text("OKSİJEN AYARI [SPACE]", center=(oksijen_x + 80, oksijen_y - 100), color="white", fontsize=20, owidth=1, ocolor="black")
        if not atik_tamamlandi and math.sqrt((player.x - kova_x)**2 + (player.y - kova_y)**2) < 150:
            screen.draw.text("ATIK İMHA [SPACE]", center=(kova_x, kova_y - 50), color="white", fontsize=20, owidth=1, ocolor="black")
        if not jen_tamamlandi and math.sqrt((player.x - jen_panel_x)**2 + (player.y - jen_panel_y)**2) < 150:
            screen.draw.text("JENERATÖR AYARI [SPACE]", center=(jen_panel_x + 50, jen_panel_y - 80), color="orange", fontsize=20, owidth=1, ocolor="black")

    elif mode == "o2_mini_oyun":
        screen.fill((10, 20, 30))
        screen.draw.text("OKSIJEN BASINCINI DENGEDE TUT!", center=(WIDTH//2, 200), fontsize=50, color=GLOW_BLUE)
        screen.draw.filled_rect(Rect((WIDTH//2 - 50, 350), (100, 400)), (30, 30, 30))
        screen.draw.filled_rect(Rect((WIDTH//2 - 50, 500), (100, 150)), (0, 120, 0)) 
        y_pos = 750 - (o2_basinc*4); screen.draw.filled_rect(Rect((WIDTH//2 - 65, y_pos), (130, 10)), RED) 
        kalan = max(0, int(o2_basari_sure - (time.time() - o2_gorev_vakti)))
        screen.draw.text(f"DAYAN: {kalan} SN", center=(WIDTH//2, 820), fontsize=50, color=WHITE)

    elif mode == "jen_mini_oyun":
        screen.fill((20, 20, 30))
        screen.draw.text("VOLTAJ SENKRONIZASYONU", center=(WIDTH//2, 200), fontsize=50, color="orange")
        screen.draw.filled_rect(Rect((WIDTH//2-300, 450), (600, 60)), (50, 50, 50))
        screen.draw.filled_rect(Rect((WIDTH//2-40, 450), (80, 60)), GREEN) 
        screen.draw.filled_rect(Rect((jen_imlec_x-5, 430), (10, 100)), RED) 
        screen.draw.text(f"BAŞARILI: {jen_basari_sayisi}/3", center=(WIDTH//2, 600), fontsize=50, color=WHITE) 

    elif mode == "atik_mini_oyun":
        screen.fill((10, 10, 25))
        for atik in dusman_atiklar: atik.draw()
        screen.draw.text(f"İMHA: {mini_oyun_skor}/15  CAN: {mini_oyun_can}", (50, 50), fontsize=40, color=WHITE)

    elif mode == "rota_mini_oyun":
        screen.fill((10, 15, 30))
        screen.draw.text("AY ROTASI KALİBRASYONU", center=(WIDTH//2, 150), fontsize=60, color="cyan")
        for i in range(4): screen.draw.text(str(target_route[i]), center=(WIDTH//2-150 + i*100, 350), fontsize=80, color=GREEN)
        for i in range(4):
            color = GLOW_BLUE if i == active_digit else WHITE
            screen.draw.text(str(player_route[i]), center=(WIDTH//2-150 + i*100, 600), fontsize=80, color=color)
            if i == active_digit: screen.draw.rect(Rect((WIDTH//2-190 + i*100, 550), (80, 100)), color)

    elif mode == "pc_okuma":
        bg3.draw()
        kutu = Rect((200, 250), (WIDTH-400, 400)); screen.draw.filled_rect(kutu, (20, 20, 30)); screen.draw.rect(kutu, "cyan")
        screen.draw.text(uzay_bilgileri[bilgi_sirasi], (250, 400), width=WIDTH-500, fontsize=35, color=WHITE)
        screen.draw.text("Devam etmek için ENTER", center=(WIDTH//2, 600), fontsize=30, color="gray")

    elif mode == "konusma":
        bg3.draw(); npc.draw(); player.draw()
        kutu = Rect((100, HEIGHT-250), (WIDTH-200, 200)); screen.draw.filled_rect(kutu, (10, 10, 10)); screen.draw.rect(kutu, GLOW_BLUE)
        screen.draw.text("KAPTAN :", (130, HEIGHT-230), fontsize=40, color=MAIN_BLUE)
        screen.draw.text("Ay'a gitmek için astronot arıyoruz. Aradığımız kişi sen olabilirsin!\nŞu testi geç ve astronot ol!\n\n(Devam etmek için ENTER)", (130, HEIGHT-180), fontsize=35, color=WHITE)

    elif mode == "gorev_gforce":
        screen.fill((20, 0, 0))
        screen.draw.text("YÜKSEK G-KUVVETİ! [SPACE] BAS!", center=(WIDTH//2 + shake_x, 200 + shake_y), fontsize=50, color=WHITE)
        screen.draw.filled_rect(Rect((WIDTH//2-200 + shake_x, 450 + shake_y), (400, 50)), (50, 0, 0))
        screen.draw.filled_rect(Rect((WIDTH//2-200 + shake_x, 450 + shake_y), (400 * (g_bari_val/100), 50)), GREEN)
        kalan = max(0, int(15 - (time.time() - g_baslangic_vakti)))
        screen.draw.text(f"DAYAN: {kalan} SN", center=(WIDTH//2 + shake_x, 600 + shake_y), fontsize=60, color=WHITE)

    elif mode == "gorev_gforce_basari":
        bg3.draw(); npc.draw(); player.draw()
        kutu = Rect((100, HEIGHT-250), (WIDTH-200, 200)); screen.draw.filled_rect(kutu, (10, 10, 10)); screen.draw.rect(kutu, GREEN)
        screen.draw.text("KAPTAN: Tebrikler testi geçtin! Gemiye transfer oluyorsun. (ENTER)", (130, HEIGHT-180), fontsize=32, color=WHITE)

    elif mode == "final_sahne":
        bg5.draw()
        overlay = pygame.Surface((WIDTH, 240)); overlay.set_alpha(180); overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, HEIGHT // 2 - 120))
        screen.draw.text("GÖREV BAŞARIYLA TAMAMLANDI!", center=(WIDTH//2, HEIGHT//2 - 30), fontsize=70, color=GREEN, shadow=(2,2))
        screen.draw.text("Ay'a güvenle iniş yaptın. İnsanlık sana minnettar!", center=(WIDTH//2, HEIGHT//2 + 40), fontsize=35, color=WHITE)
        screen.draw.text("ENTER'a bas", center=(WIDTH//2, HEIGHT - 100), fontsize=25, color="gray")

    elif mode == "bg6_son":
        bg6.draw()
        screen.draw.text("Haberleri izlemek için ENTER'a bas", center=(WIDTH//2, HEIGHT - 40), fontsize=20, color="gray")

    # --- YENİ EKLENEN BG7 DRAW MANTIĞI ---
    elif mode == "bg7_ekran":
        bg7.draw()

        screen.draw.text("Ana menüye dönmek için ENTER'a bas", center=(WIDTH//2, HEIGHT - 40), fontsize=20, color="gray")

    elif mode == "game_over":
        screen.fill((50, 0, 0)); screen.draw.text("BAŞARISIZ", center=(WIDTH//2, 350), fontsize=100, color=WHITE)
        btn_tekrar = Rect((WIDTH//2-150, 500), (300, 80)); screen.draw.filled_rect(btn_tekrar, WHITE); screen.draw.text("MENÜ", center=btn_tekrar.center, fontsize=40, color=RED)

    if mode not in ["intro", "menu", "bilgi", "final_sahne", "bg6_son", "bg7_ekran"]:
        screen.draw.text(f"GÜÇ SEVİYESİ: %{int(guc_bari)}", (50, 20), fontsize=40, color=GLOW_BLUE, shadow=(1,1))

    if fade_alfa > 0:
        s = pygame.Surface((WIDTH, HEIGHT)); s.set_alpha(fade_alfa); s.fill((0, 0, 0)); screen.blit(s, (0,0))

# =====================================================================
# --- OLAYLAR ---
# =====================================================================
def on_key_down(key):
    global mode, g_bari_val, last_g_press_time, fade_baslasin, bilgi_sirasi, g_baslangic_vakti, fade_hedef
    global o2_basinc, o2_gorev_vakti, jen_basari_sayisi, jen_hiz, atik_tamamlandi, o2_tamamlandi, jen_tamamlandi, guc_bari
    global rota_tamamlandi, target_route, player_route, active_digit, test_gechildi

    if mode == "oyun" and key == keys.SPACE:
        if math.sqrt((player.x - pc_egitim_x)**2 + (player.y - pc_egitim_y)**2) < 180: mode = "pc_okuma"; bilgi_sirasi = 0
        elif math.sqrt((player.x - npc.x)**2 + (player.y - npc.y)**2) < 200: mode = "konusma"
    
    elif mode == "uzay_gemisi" and key == keys.SPACE:
        if not rota_tamamlandi and math.sqrt((player.x - pc_gemi_x)**2 + (player.y - pc_gemi_y)**2) < 150:
            target_route = [random.randint(1,9) for _ in range(4)]; player_route = [0,0,0,0]; active_digit = 0; mode = "rota_mini_oyun"
        elif not atik_tamamlandi and math.sqrt((player.x - kova_x)**2 + (player.y - kova_y)**2) < 150:
            global mini_oyun_skor, mini_oyun_can; mini_oyun_skor = 0; mini_oyun_can = 3; dusman_atiklar.clear(); mode = "atik_mini_oyun"
        elif not o2_tamamlandi and math.sqrt((player.x - oksijen_x)**2 + (player.y - oksijen_y)**2) < 150:
            o2_basinc = 50; o2_gorev_vakti = time.time(); mode = "o2_mini_oyun"
        elif not jen_tamamlandi and math.sqrt((player.x - jen_panel_x)**2 + (player.y - jen_panel_y)**2) < 150:
            jen_basari_sayisi = 0; jen_hiz = 10; mode = "jen_mini_oyun"

    elif mode == "rota_mini_oyun":
        if key == keys.LEFT: active_digit = (active_digit - 1) % 4
        elif key == keys.RIGHT: active_digit = (active_digit + 1) % 4
        elif key == keys.UP: player_route[active_digit] = (player_route[active_digit] + 1) % 10
        elif key == keys.DOWN: player_route[active_digit] = (player_route[active_digit] - 1) % 10
        elif key == keys.RETURN:
            if player_route == target_route: 
                guc_bari = min(100, guc_bari + 25) 
                rota_tamamlandi = True; mode = "uzay_gemisi"
            else: mode = "uzay_gemisi"

    elif mode == "jen_mini_oyun" and key == keys.SPACE:
        if WIDTH // 2 - 40 < jen_imlec_x < WIDTH // 2 + 40:
            jen_basari_sayisi += 1; jen_hiz += 4
            if jen_basari_sayisi >= 3: 
                guc_bari = min(100, guc_bari + 25) 
                jen_tamamlandi = True; mode = "uzay_gemisi"
        else: mode = "uzay_gemisi"

    elif mode == "pc_okuma" and key == keys.RETURN:
        bilgi_sirasi += 1
        if bilgi_sirasi >= len(uzay_bilgileri): mode = "oyun"

    elif mode == "konusma" and key == keys.RETURN:
        mode = "gorev_gforce"; g_baslangic_vakti = time.time(); g_bari_val = 100

    elif mode == "gorev_gforce" and key == keys.SPACE:
        curr = time.time()
        if curr - last_g_press_time >= 0.15: g_bari_val = min(100, g_bari_val + 18); last_g_press_time = curr

    elif mode == "gorev_gforce_basari" and key == keys.RETURN:
        test_gechildi = True
        fade_baslasin = True; fade_hedef = "uzay_gemisi"

    elif mode == "final_sahne" and key == keys.RETURN:
        fade_baslasin = True
        fade_hedef = "bg6_son"

    # --- BG6_SONDAN SONRA BG7'YE GEÇİŞ ---
    elif mode == "bg6_son" and key == keys.RETURN:
        fade_baslasin = True
        fade_hedef = "bg7_ekran"

    # --- BG7'DEN SONRA MENÜYE DÖNÜŞ ---
    elif mode == "bg7_ekran" and key == keys.RETURN:
        # Oyunu sıfırla
        guc_bari = 0; atik_tamamlandi = o2_tamamlandi = jen_tamamlandi = rota_tamamlandi = False
        test_gechildi = False
        player.image = "player" 
        mode = "menu"

def on_mouse_down(pos):
    global mode, mini_oyun_skor, shake_amount
    if mode == "menu":
        if Rect((WIDTH//2-150, 420), (300, 70)).collidepoint(pos): mode = "oyun"
        elif Rect((WIDTH//2-150, 510), (300, 70)).collidepoint(pos): mode = "bilgi"
        elif Rect((WIDTH//2-150, 600), (300, 70)).collidepoint(pos): exit()
    elif mode == "bilgi":
        if Rect((WIDTH//2-100, 700), (200, 50)).collidepoint(pos): mode = "menu"
    elif mode == "game_over":
        if Rect((WIDTH//2-150, 500), (300, 80)).collidepoint(pos): mode = "menu"
    elif mode == "atik_mini_oyun":
        for atik in dusman_atiklar[:]:
            if atik.collidepoint(pos):
                dusman_atiklar.remove(atik); mini_oyun_skor += 1; shake_amount = 10

pgzrun.go()