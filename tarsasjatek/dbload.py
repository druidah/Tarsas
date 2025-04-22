#kártya és mező adatbázis feltöltő szkript

from tarsasjatek.models import Tile, Card
#a játék belső mechanikája közben megváltozott de az adatbázist így hagytam.
def create_tiles():
    tiles_data = [
        (1, "Start", "gain_school_point|get_dog|get_job"),
        (2, "Általános iskola kezdete", "start_primary_school"),
        (3, "Tájékozódás órán fehérbotot kapsz", "get_white_cane"),
        (4, "Vakvezető kutya igénylés", "request_guide_dog"),
        (5, "Szülinapod van!", "draw_card"),
        (6, "Középiskola kezdete", "start_high_school|gain_school_point"),
        (7, "Névnapod van!", "draw_card"),
        (8, "Valaki rád kiabált!", "draw_card"),
        (9, "Utcai zenész munkalehetőség", "work_musician"),
        (10, "Megtanultál zenélni!", "gain_music_skill"),
        (11, "Hangszert vásároltál", "buy_instruments"),
        (12, "Egyetem kezdete", "start_university|gain_school_point"),
        (13, "Egyetemi buli", "draw_card_inuni"),
        (14, "Szőnyegszövő munkalehetőség", "work_weaver"),
        (15, "Zenészi gondolatok", "go_to_tile_10"),
        (16, "Programozó munkalehetőség", "work_programmer"),
        (17, "Életed változik!", "draw_card"),
        (18, "Tanulmányok folytatása", "go_to_school"),
        (19, "Rossz társaságba keveredtél!", "lose_school_point"),
        (20, "Elhagytad a fehérbotodat!", "lose_white_cane"),
    ]
    
    for num, desc, effect in tiles_data:
        Tile.objects.create(number=num, description=desc, effect=effect)

#itt is tök mindegy a kártya effect, nem használom már.
def create_cards():
    cards_data = [
        ("Sikeres vizsga!", "gain_school_point"),
        ("Rossz felelet!", "lose_school_point"),
        ("Ajándék fehérbot!", "get_white_cane"),
        ("Ajándék hangszer!", "get_instrument"),
        ("Kirúgtak a munkából!", "lose_job"),
        ("Vakvezető kutyád elhunyt!", "lose_guide_dog"),
        ("Szüleid erőltetik a zenét!", "go_to_tile_10"),
        ("Kutyád beteg lett!", "skip_turn_for_guide_dog_care"),
        ("Tovább szeretnél tanulni!", "continue_learning"),
        ("Eltört a fehérbotod!", "Lose_Cane"),
        ("Elgondolkozol egy vakvezető kutya igénylésén!", "Get_dog"),
        ("Megkapod a várt munkát!", "Get_Job"),
    ]
    
    for desc, effect in cards_data:
        Card.objects.create(description=desc, effect=effect)

def run():
    create_tiles()
    create_cards()
    print("Adatok feltöltve!")
