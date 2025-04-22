from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    position = models.IntegerField(default=1)
    
    # Iskolák és pontok
    school_points = models.IntegerField(default=0)
    has_primary_school = models.BooleanField(default=False)  # Általános iskola elvégezve?
    has_high_school = models.BooleanField(default=False)  # Középiskola elvégezve?
    has_university = models.BooleanField(default=False)  # Egyetem elvégezve?
    in_primary_school = models.BooleanField(default=False)  # Általános iskolát tanulja?
    in_high_school = models.BooleanField(default=False)  # Középiskolát tanulja?
    in_university = models.BooleanField(default=False)  # Egyetemet tanulja?
    
    # Egyéb tulajdonságok
    has_white_cane = models.BooleanField(default=False)
    has_guide_dog = models.BooleanField(default=False)
    has_instrument = models.BooleanField(default=False)
    knows_music = models.BooleanField(default=False)
    job = models.CharField(max_length=100, blank=True, null=True)
    skip_turn = models.BooleanField(default=False)
    waiting_for_dog = models.BooleanField(default=False)

    waiting_for_job = models.CharField(max_length=50, null=True, blank=True)
    just_crossed_start = models.BooleanField(default=False)  

    def __str__(self):
        return self.name

    def move(self, steps):
        """Játékos mozgatása a táblán körbe-körbe, a start mezőn való áthaladás figyelembe vételével."""
        board_size = Tile.objects.count()
        prev_position = self.position

        self.position += steps
        if self.position > board_size:
            self.position = self.position % board_size  

        self.just_crossed_start = prev_position > self.position

        self.check_education_progress()
        self.save()

    def check_education_progress(self):
        """Ellenőrzi, hogy az iskolai pontok alapján befejezhetők-e az iskolák és nullázza a pontokat."""
        if self.in_primary_school and self.school_points >= 1:
            self.has_primary_school = True
            self.in_primary_school = False  # Már nem tanulja
            self.school_points = 0  # Iskolapontok nullázása

        if self.in_high_school and self.school_points >= 2:
            self.has_high_school = True
            self.in_high_school = False
            self.school_points = 0  # Iskolapontok nullázása
        if self.in_university and self.school_points >= 3:
            self.has_university = True
            self.in_university = False
            self.school_points = 0  # Iskolapontok nullázása
        self.save()

    def start_school(self, school_type):
        """Elkezdi az adott iskolát, ha lehetséges."""
        if school_type == "primary" and not self.has_primary_school:
            self.in_primary_school = True
        elif school_type == "high" and self.has_primary_school and not self.has_high_school:
            self.in_high_school = True
        elif school_type == "university" and self.has_high_school and not self.has_university:
            self.in_university = True
        self.save()

class Tile(models.Model):
    number = models.IntegerField(unique=True)
    description = models.TextField()
    effect = models.TextField(blank=True, null=True) #már nem használom

    def __str__(self):
        return f"Tile {self.number}: {self.description}"

class Game(models.Model):
    current_turn = models.IntegerField(default=0)
    players = models.ManyToManyField(Player)
    log = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Game {self.id}"
    def next_turn(self):
        """Következő játékos lépése."""
        self.current_turn = (self.current_turn + 1) % self.players.count()
        self.save()

class Card(models.Model):
    description = models.TextField()
    effect = models.TextField() #lényegtelen már

    def __str__(self):
        return f"Card: {self.description}"


