from django.shortcuts import render, redirect, get_object_or_404
import random
from django.http import HttpResponse
from .models import Game, Card, Player, Tile

def home(request):
    return render(request, 'home.html')

def game_rules(request):
    return render(request, 'gamerules.html')


def new_game(request):
    if request.method == "POST":
        player_count = int(request.POST.get("player_count"))
        player_names = [request.POST.get(f"player_{i}") for i in range(1, player_count + 1)]
        
        if not all(name.strip() for name in player_names):
            return HttpResponse("Minden játékosnak meg kell adni a nevét!", status=400) # Ez szerintem már sehogy nem triggerelődhet

        # Új játék létrehozása
        game = Game.objects.create()

        # Játékosok hozzáadása
        players = []
        for name in player_names:
            player = Player.objects.create(name=name.strip())  
            players.append(player)
        
        game.players.set(players)  
        game.save()

        return redirect("game_view", game_id=game.id)

    return render(request, "home.html")


def game_view(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    players = Player.objects.filter(game=game)
    current_player = players[game.current_turn % len(players)]
    current_tile = Tile.objects.get(number=current_player.position)
    tiles = {tile.number: tile for tile in Tile.objects.all()}

    # Nyertes ellenőrzése
    if check_win_condition(current_player):
        return HttpResponse(f"{current_player.name} nyert! Gratulálunk!", status=200) #Ronda, át kell majd írni.

    return render(request, "game_view.html", {
        "game": game,
        "players": players,
        "current_player": current_player,
        "current_tile": current_tile,
        "tiles": tiles,  
    })

def roll_dice(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    players = Player.objects.filter(game=game)
    current_player = players[game.current_turn % len(players)]

    if not current_player.skip_turn:
        dice_result = random.randint(1, 6)
        current_player.move(dice_result)

        if game.log is None: #át kéne írni hogy ne legyen none.
            game.log = ""
        game.log += f"{current_player.name} dobott {dice_result}-t, és a {current_player.position}. mezőre lépett.\n"

        handle_tile_effect(current_player, game)  # Új tile effect függvény, nem számít az adatbázisban elfoglalt helye
        if current_player.just_crossed_start and current_player.waiting_for_job == "szőnyegszövő":
            current_player.job = "szőnyegszövő"
            current_player.waiting_for_job = ""
            current_player.save()
    else:
        current_player.skip_turn = False
    current_player.just_crossed_start = False
    current_player.save()
    game.current_turn += 1


    game.save()
    return redirect("game_view", game_id=game.id)

def handle_tile_effect(player, game):
    """Kezeli a mezőkre lépés hatásait."""
    tile_effects = {
        1: lambda p: check_start_effects(p),
        2: lambda p: (increase_primary(p), p.start_school("primary")),
        3: lambda p: receive_white_cane(p),
        4: lambda p: request_guide_dog(p),
        5: lambda p: draw_event_card(p, game),
        6: lambda p: (increase_high(p), p.start_school("high")),
        7: lambda p: draw_event_card(p, game),
        8: lambda p: draw_event_card(p, game),
        9: lambda p: start_work(p, "street_musician"),
        10: lambda p: learn_music(p),
        11: lambda p: purchase_instrument(p),
        12: lambda p: (increase_uni(p), p.start_school("university")),
        13: lambda p: draw_event_card_if_in_university(p, game),
        14: lambda p: start_work(p, "weaver"),
        15: lambda p: go_to_music(p, game),
        16: lambda p: start_work(p, "programmer"),
        17: lambda p: draw_event_card(p, game),
        18: lambda p: continue_education(p, game),
        19: lambda p: decrease_school_points_bad_people(p),
        20: lambda p: lose_white_cane(p),
    }
    
    effect = tile_effects.get(player.position)
    if effect:
        effect(player)
        player.save()

def check_start_effects(player):
    """A Start mező speciális szabályait kezeli."""
    if player.in_primary_school:
        player.school_points += 1
    elif player.in_high_school:
        player.school_points += 1
    elif player.in_university:
        player.school_points += 1
    
    if player.waiting_for_dog:
        player.has_guide_dog = True
        player.waiting_for_dog = False
    if player.waiting_for_job == "programozó":
        player.job = "programozó"


    player.check_education_progress()
    player.save()

def decrease_school_points(player):
    """Csökkenti az iskolapontokat."""
    player.school_points = max(0, player.school_points - 1)
    player.save()

def handle_event_card(player, game):
    """A szerencsekártyák hatásait kezeli."""
    card_effects = {
        1: lambda p: increase_school_points(p),
        2: lambda p: decrease_school_points(p),
        3: lambda p: receive_white_cane(p),
        4: lambda p: get_instrument(p),
        5: lambda p: lose_job(p),
        6: lambda p: lose_guide_dog(p),
        7: lambda p: move_to_music_school(p),
        8: lambda p: skip_turn_for_guide_dog_care(p),
        9: lambda p: continue_education(p, game),
        10: lambda p: lose_white_cane(p),
        11: lambda p: request_guide_dog(p),
        12: lambda p: get_wanted_job(p),

    }

    effect = card_effects.get(player.drawn_card)
    if effect:
        effect(player)
        player.save()

def draw_event_card(player, game):
#meg kellene csinálni hogy egy kártya csak egyszer legyen benne a halmazban, utána keverje újra ha elfogy. Todo.
    card = Card.objects.order_by('?').first()
    player.drawn_card = card.id
    handle_event_card(player, game)
    player.save() #redundáns
    if game.log is None:
        game.log = ""
    game.log += f"{player.name} húzott egy szerencsekártyát: {card.description}\n"
    game.save()

def draw_event_card_if_in_university(player, game):
    if player.in_university:
        draw_event_card(player, game)


def receive_white_cane(player):
    player.has_white_cane = True
    player.save() #redundáns

def get_instrument(player):
    player.has_instrument = True
    player.save() #itt is 

def lose_job(player):
    if player.job != "utcazenész":
        player.job = None
    player.save()

def lose_guide_dog(player):
    player.has_guide_dog = False
    player.save()

def move_to_music_school(player):
    if player.knows_music:
        pass
    player.position = 10
    learn_music(player)
    player.save()

def learn_music(player):
    if player.in_primary_school or player.in_high_school or player.in_university:
        player.knows_music = True
        player.save()

def increase_school_points(player):
    if player.in_primary_school or player.in_high_school or player.in_university:
        player.school_points = player.school_points+1
        player.save()

def request_guide_dog(player):
    """Vakvezető kutya igénylése."""
    if player.has_guide_dog:
        return  # Ha már van kutyája, nincs teendő

    if player.waiting_for_dog:
        player.has_guide_dog = True
        player.waiting_for_dog = False  
    elif player.has_primary_school:  
        player.waiting_for_dog = True
    
    player.save()  

def skip_turn_for_guide_dog_care(player):
    if player.has_guide_dog:
        player.skip_turn = True
        player.save()

def start_work(player, work_type):
    if player.job != "":
        pass
    if work_type == "street_musician":
        if player.knows_music == True and player.has_instrument == True:
            player.job = "utcazenész"
            player.waiting_for_job = ""
            player.save()

    elif work_type == "weaver":
        # Csak akkor lehet szőnyegszövő, ha kész a középiskola
        if player.has_high_school:
            player.waiting_for_job = "szőnyegszövő"
            player.save()

    elif work_type == "programmer":
        # Csak akkor lehet programozó, ha kész az egyetem
        if player.has_university:
            if player.position == 16:
                player.job = "programozó"
                player.waiting_for_job = ""
            else:
                player.waiting_for_job = "programozó"
            player.save()

def check_win_condition(player):
    """Ellenőrzi, hogy a játékos nyert-e."""
    if player.job !=  "" and player.has_guide_dog and player.has_white_cane:
        return True
    return False

def purchase_instrument(player):
    if player.has_instrument == False:
        player.has_instrument = True
        player.skip_turn = True
        player.save()

def lose_white_cane(player):
    player.has_white_cane = False
    player.save()

def continue_education(player, game):
    if player.has_primary_school == False:
        player.position = 2
        handle_tile_effect(player, game)  
        player.save()
    elif player.in_high_school or player.has_primary_school:
        player.position = 6
        handle_tile_effect(player, game)  
        player.save()
    elif player.in_university or player.has_high_school:
        player.position =12 
        handle_tile_effect(player, game)  
        player.save()

def increase_primary(player):
    if player.in_primary_school:
        player.school_points += 1
        player.save()

def increase_high(player):
    if player.in_high_school:
        player.school_points += 1
        player.save()

def increase_uni(player):
    if player.in_university:
        player.school_points += 1
        player.save()

def go_to_music(player, game):
    if player.knows_music == False:
        player.position = 10
        handle_tile_effect(player, game)
        player.save()

def decrease_school_points_bad_people(player):
    player.school_points -= 1
    if player.school_points < 0:
        player.in_primary_school = False
        player.in_high_school = False
        player.in_university = False
    player.save()

def get_wanted_job(player):
    if player_waiting_for_job == "szőnyegszövő":
        player.job = "szőnyegszövő"
        player.waiting_for_job = ""
        player.save()
    elif player.waiting_for_job == "programozó":
        player.job = "programozó"
        player.waiting_for_job = ""
        player.save()
            