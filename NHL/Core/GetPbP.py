import urllib.request
import os.path
import time
import http.client
import re
import os

__author__ = 'muneebalam'

MAX_SEASON = 2015
MONTHS = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7,
          'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
TEAM_MAP = {'ATLANTA THRASHERS': 'ATL', 'WASHINGTON CAPITALS': 'WSH', 'CAROLINA HURRICANES': 'CAR',
            'TAMPA BAY LIGHTNING': 'T.B', 'FLORIDA PANTHERS': 'FLA', 'PITTSBURGH PENGUINS': 'PIT',
            'PHILADELPHIA FLYERS': 'PHI', 'NEW YORK RANGERS': 'NYR', 'NEW YORK ISLANDERS': 'NYI',
            'NEW JERSEY DEVILS': 'N.J', 'BOSTON BRUINS': 'BOS', 'MONTREAL CANADIENS': 'MTL',
            'CANADIENS MONTREAL': 'MTL', 'OTTAWA SENATORS': 'OTT', 'BUFFALO SABRES': 'BUF',
            'TORONTO MAPLE LEAFS': 'TOR', 'DETROIT RED WINGS': 'DET', 'CHICAGO BLACKHAWKS': 'CHI',
            'ST. LOUIS BLUES': 'STL', 'NASHVILLE PREDATORS': 'NSH', 'MINNESOTA WILD': 'MIN', 'VANCOUVER CANUCKS': 'VAN',
            'EDMONTON OILERS': 'EDM', 'CALGARY FLAMES': 'CGY', 'WINNIPEG JETS': 'WPG',
            'COLORADO AVALANCHE': 'COL', 'COLUMBUS BLUE JACKETS': 'CBJ', 'SAN JOSE SHARKS': 'S.J',
            'LOS ANGELES KINGS': 'L.A', 'ANAHEIM DUCKS': 'ANA', 'DALLAS STARS': 'DAL',
            'PHOENIX COYOTES': 'PHX', 'ARIZONA COYOTES': 'ARI', 'EASTERN': 'EAS', 'WESTERN': 'WES',
            'TEAM LIDSTROM': 'ASB', 'TEAM STAAL': 'ASR', 'TEAM CHARA': 'BLU', 'TEAM ALFREDSSON': 'RED',
            'ATLANTIC': 'ATL', 'METROPOLITAN': 'MET', 'PACIFIC': 'PAC', 'CENTRAL': 'CEN'}
MASCOT_NAMES = {'ATLANTA THRASHERS': 'Thrashers', 'ATL': 'Thrashers',
                'WASHINGTON CAPITALS': 'Capitals', 'WSH': 'Capitals',
                'CAROLINA HURRICANES': 'Hurricanes', 'CAR': 'Hurricanes',
                'TAMPA BAY LIGHTNING': 'Lightning', 'T.B': 'Lightning',
                'FLORIDA PANTHERS': 'Panthers', 'FLA': 'Panthers',
                'PITTSBURGH PENGUINS': 'Penguins', 'PIT': 'Penguins',
                'PHILADELPHIA FLYERS': 'Flyers', 'PHI': 'Flyers',
                'NEW JERSEY DEVILS': 'Devils', 'N.J': 'Devils',
                'NEW YORK ISLANDERS': 'Islanders', 'NYI': 'Islanders',
                'NEW YORK RANGERS': 'Rangers', 'NYR': 'Rangers',
                'BOSTON BRUINS': 'Bruins', 'BOS': 'Bruins',
                'MONTREAL CANADIENS': 'Canadiens', 'MTL': 'Canadiens', 'CANADIENS MONTREAL': 'Canadiens',
                'TORONTO MAPLE LEAFS': 'Maple Leafs', 'TOR': 'Maple Leafs',
                'OTTAWA SENATORS': 'Senators', 'OTT': 'Senators',
                'BUFFALO SABRES': 'Sabres', 'BUF': 'Sabres',
                'DETROIT RED WINGS': 'Red Wings', 'DET': 'Red Wings',
                'COLUMBUS BLUE JACKETS': 'Blue Jackets', 'CBJ': 'Blue Jackets',
                'CHICAGO BLACKHAWKS': 'Blackhawks', 'CHI': 'Blackhawks',
                'NASHVILLE PREDATORS': 'Predators', 'NSH': 'Predators',
                'ST. LOUIS BLUES': 'Blues', 'STL': 'Blues',
                'MINNESOTA WILD': 'Wild', 'MIN': 'Wild',
                'EDMONTON OILERS': 'Oilers', 'EDM': 'Oilers',
                'CALGARY FLAMES': 'Flames', 'CGY': 'Flames',
                'VANCOUVER CANUCKS': 'Canucks', 'VAN': 'Canucks',
                'COLORADO AVALANCHE': 'Avalanche', 'COL': 'Avalanche',
                'WINNIPEG JETS': 'Jets', 'WPG': 'Jets',
                'PHOENIX COYOTES': 'Coyotes', 'PHX': 'Coyotes',
                'ARIZONA COYOTES': 'Coyotes', 'ARI': 'Coyotes',
                'DALLAS STARS': 'Stars', 'DAL': 'Stars',
                'LOS ANGELES KINGS': 'Kings', 'L.A': 'Kings',
                'ANAHEIM DUCKS': 'Ducks', 'ANA': 'Ducks',
                'SAN JOSE SHARKS': 'Sharks', 'S.J': 'Sharks',
                'EASTERN': 'Eastern All-Stars', 'EAS': 'Eastern All-Stars',
                'WESTERN': 'Western All-Stars', 'WES': 'Western All-Stars',
                'TEAM LIDSTROM': 'Team Lidstrom', 'ASB': 'Team Lidstrom',
                'TEAM STAAL': 'Team Staal', 'ASR': 'Team Staal',
                'TEAM CHARA': 'Team Chara', 'BLU': 'Team Chara',
                'ATLANTIC': 'Team Atlantic', 'METROPOLITAN': 'Team Metropolitan',
                'CENTRAL': 'Team Central', 'PACIFIC': 'Team Pacific'}
TEAMS = {abbrev for abbrev in TEAM_MAP.values()}
DAYS = {'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'}
DAYS_SHORT = {day[:3] for day in DAYS}
EVENT_TYPES = {'PSTR': 'Period start', 'PEND': 'Period end', 'GEND': 'Game end', 'FAC': 'Faceoff', 'HIT': 'Hit',
               'BLOCK': 'Block', 'SHOT': 'Shot', 'MISS': 'Miss', 'GOAL': 'Goal', 'PENL': 'Penalty', 'STOP': 'Stop',
               'GIVE': 'Giveaway', 'TAKE': 'Takeaway', 'EISTR': 'Early Intermission Start',
               'EIEND': 'Early Intermission End', 'SOC': 'Shootout Completed', 'GOFF': '', 'CHL': 'Challenge'}
EVENT_HELPER = {'PSTR': -4, 'PEND': -4, 'GEND': -4, 'FAC': -5, 'HIT': -5, 'BLOCK': -5, 'SHOT': -5, 'MISS': -5,
                'GOAL': -5, 'PENL': -5, 'STOP': -4, 'GIVE': -5, 'TAKE': -5, 'EISTR': -4, 'EIEND': -4, 'SOC': -5,
                'GOFF': -4, 'CHL': -5}
ZONES = {'Off', 'Neu', 'Def', 'Off.', 'Neu.', 'Def.'}
POSITIONS = {'L', 'C', 'R', 'D', 'G', 'F'}
POSITIONS2 = {'Left Wing', 'Center', 'Right Wing', 'Defense', 'Goalie', 'Forward'}
PENALTIES = {'Holding the stick': 'Holding the stick', 'Slashing': 'Slashing', 'Roughing': 'Roughing',
             'Holding': 'Holding', 'Tripping': 'Tripping', 'Hooking': 'Hooking', 'Interference': 'Interference',
             'Cross checking': 'Cross checking', 'Boarding': 'Boarding', 'Hi-sticking': 'High-sticking',
             'Elbowing': 'Elbowing', 'Unsportsmanlike conduct': 'Unsportsmanlike conduct',
             'Interference on goalkeeper': 'Goalie interference', 'Too many men/ice - bench': 'Too many men-bench',
             'Delaying Game-Puck over glass': 'Delay of game-puck over glass',
             'Closing hand on puck': 'Delay of game-Smothering puck', 'Fighting': 'Fighting', 'Spearing': 'Spearing',
             'Abuse of officials': 'Abusive language', 'Diving': 'Diving', 'Embellishment': 'Diving',
             'Hi stick - double minor': 'High-sticking', 'Illegal check to head': 'Illegal check to head',
             'Charging': 'Charging', 'PS-Hooking on breakaway': 'PS-Hooking on breakaway',
             'PS-Tripping on breakaway': 'PS-Tripping on breakaway',
             'PS-Covering puck in crease': 'PS-Covering puck in crease',
             'PS - Slash on breakaway': 'PS-Slashing on breakaway',
             'PS-Slash on breakaway': 'PS-Slasing on breakaway',
             'PS - Covering puck in crease': 'PS-Covering puck in crease',
             'PS-Net displaced': 'PS-Net displaced',
             'PS - Throw object at puck': 'PS-Throw object at puck',
             'PS-Throw object at puck': 'PS-Throw object at puck',
             'PS - Picking up puck in crease': 'PS-Picking up puck in crease',
             'Delay Gm - Face-off Violation': 'Delay of game-faceoff violation',
             'Delaying the game': 'Delay of game',
             'Delay of game': 'Delay of game', 'Abusive language - Misconduct': 'Abusive language-Misconduct',
             'Abusive language - bench': 'Abusive language-bench',
             'Kneeing': 'Kneeing', 'Game misconduct': 'Game misconduct', 'Misconduct': 'Misconduct',
             'Game Misconduct': 'Game misconduct',
             'Throwing stick': 'Throwing stick', 'Instigator - face shield': 'Instigator-face shield',
             'Objects on ice - bench': 'Objects on ice-bench', 'Goalie leave crease': 'Delay of game-Ill. play goalie',
             'Delaying Game-Ill. play goalie': 'Delay of game-Ill. play goalie', 'n/a': 'n/a',
             'Delaying Game-Smothering puck': 'Delay of game-Smothering puck', 'Concealing puck': 'Concealing puck',
             'Instigator': 'Instigator', 'Broken stick': 'Broken stick', 'Clipping': 'Clipping',
             'Match penalty': 'Match penalty', 'Illegal stick': 'Illegal stick', 'Butt ending': 'Butt-ending',
             'Checking from behind': 'Checking from behind', "Leaving player's/penalty bench": "Leaving bench",
             'Player leaves bench - bench': 'Leaving bench-bench', 'Illegal equipment': 'Illegal equipment',
             'Aggressor': 'Instigator', 'Illegal substitution - bench': 'Illegal substitution-bench',
             'Cross check - double minor': 'Cross checking', 'Face-off violation': 'Delay of game-faceoff violation',
             'Leaving penalty box - bench': 'Leaving penalty box-bench', 'Head butting': 'Head butting'}
NAMES = {'n/a': 'n/a', 'ALEXANDER OVECHKIN': 'Alex Ovechkin', 'TOBY ENSTROM': 'Tobias Enstrom',
         'JAMIE MCGINN': 'Jamie McGinn', 'CODY MCLEOD': 'Cody McLeod', 'MARC-EDOUARD VLASIC': 'Marc-Edouard Vlasic',
         'RYAN MCDONAGH': 'Ryan McDonagh', 'CHRIS TANEV': 'Christopher Tanev', 'JARED MCCANN': 'Jared McCann',
         'P.K. SUBBAN': 'PK Subban', 'DEVANTE SMITH-PELLY': 'Devante Smith-Pelly', 'MIKE MCKENNA': 'Mike McKenna',
         'MICHAEL MCCARRON': 'Michael McCarron', 'T.J. BRENNAN': 'TJ Brennan', 'BRAYDEN MCNABB': 'Brayden McNabb',
         'PIERRE-ALEXANDRE PARENTEAU': 'PA Parenteau', 'JAMES VAN RIEMSDYK': 'James van Riemsdyk',
         'OLIVER EKMAN-LARSSON': 'Oliver Ekman-Larsson', 'TJ OSHIE': 'TJ Oshie', 'J P DUMONT': 'JP Dumont',
         'J.T. MILLER': 'JT Miller', 'R.J UMBERGER': 'RJ Umberger', 'PA PARENTEAU': 'PA Parenteau',
         'PER-JOHAN AXELSSON': 'PJ Axelsson', 'MAXIME TALBOT': 'Max Talbot', 'JOHN-MICHAEL LILES': 'John-Michael Liles',
         'DANIEL GIRARDI': 'Dan Girardi', 'DANIEL CLEARY': 'Dan Cleary', 'NIKLAS KRONVALL': 'Niklas Kronwall',
         'SIARHEI KASTSITSYN': 'Sergei Kostitsyn', 'ANDREI KASTSITSYN': 'Andrei Kostitsyn',
         'ALEXEI KOVALEV': 'Alex Kovalev', 'DAVID JOHNNY ODUYA': 'Johnny Oduya', 'EDWARD PURCELL': 'Teddy Purcell',
         'NICKLAS GROSSMAN': 'Nicklas Grossmann', 'PERNELL KARL SUBBAN': 'PK Subban', 'VOJTEK VOLSKI': 'Wojtek Wolski',
         'VYACHESLAV VOYNOV': 'Slava Voynov', 'FREDDY MODIN': 'Fredrik Modin', 'VACLAV PROSPAL': 'Vinny Prospal',
         'KRISTOPHER LETANG': 'Kris Letang', 'PIERRE ALEXANDRE PARENTEAU': 'PA Parenteau', 'T.J. OSHIE': 'TJ Oshie',
         'JOHN HILLEN III': 'Jack Hillen', 'BRANDON CROMBEEN': 'BJ Crombeen', 'JEAN-PIERRE DUMONT': 'JP Dumont',
         'RYAN NUGENT-HOPKINS': 'Ryan Nugent-Hopkins', 'CONNOR MCDAVID': 'Connor McDavid',
         'TREVOR VAN RIEMSDYK': 'Trevor van Riemsdyk', 'CALVIN DE HAAN': 'Calvin de Haan', 'GREG MCKEGG': 'Greg McKegg',
         'NATHAN MACKINNON': 'Nathan MacKinnon', 'KYLE MCLAREN': 'Kyle McLaren', 'ADAM MCQUAID': 'Adam McQuaid',
         'DYLAN MCILRATH': 'Dylan McIlrath', 'DANNY DEKEYSER': 'Danny DeKeyser', 'JAKE MCCABE': 'Jake McCabe',
         'JAMIE MCBAIN': 'Jamie McBain', 'PIERRE-MARC BOUCHARD': 'Pierre-Marc Bouchard',
         'JEAN-FRANCOIS JACQUES': 'JF Jacques', 'OLE-KRISTIAN TOLLEFSEN': 'Ole-Kristian Tollefsen',
         'MARC-ANDRE BERGERON': 'Marc-Andre Bergeron', 'MARC-ANTOINE POULIOT': 'Marc-Antoine Pouliot',
         'MARC-ANDRE GRAGNANI': 'Marc-Andre Gragnani', 'JORDAN LAVALLEE-SMOTHERMAN': 'Jordan Lavallee-Smotherman',
         'PIERRE-LUC LETOURNEAU-LEBLOND': 'Pierre Leblond', 'J-F JACQUES': 'JF Jacques',
         'MARC-ANDRE CLICHE': 'Marc-Andre Cliche', 'J-P DUMONT': 'JP Dumont', 'JOSHUA BAILEY': 'Josh Bailey',
         'OLIVIER MAGNAN-GRENIER': 'Olivier Magnan-Grenier', 'FRÉDÉRIC ST-DENIS': 'Frederic St-Denis',
         'MARC-ANDRE BOURDON': 'Marc-Andre Bourdon', 'PIERRE-CEDRIC LABRIE': 'Pierre-Cedric Labrie',
         'JONATHAN AUDY-MARCHESSAULT': 'Jonathan Audy-Marchessault', 'JEAN-GABRIEL PAGEAU': 'Jean-Gabriel Pageau',
         'JEAN-PHILIPPE COTE': 'Jean-Philippe Cote', 'PIERRE-EDOUARD BELLEMARE': 'Pierre-Edouard Bellemare',
         'COLIN (JOHN) WHITE': 'Colin White', 'BATES (JON) BATTAGLIA': 'Bates Battaglia', 'MATHEW DUBMA': 'Matt Dumba',
         'NIKOLAI ANTROPOV': 'Nik Antropov', 'KRYS BARCH': 'Krystofer Barch', 'CAMERON BARKER': 'Cam Barker',
         'NICKLAS BERGFORS': 'Niclas Bergfors', 'ROBERT BLAKE': 'Rob Blake', 'MICHAEL BLUNDEN': 'Mike Blunden',
         'CHRISTOPHER BOURQUE': 'Chris Bourque', 'MICHÃ«L BOURNIVAL': 'Michael Bournival',
         'NICHOLAS BOYNTON': 'Nick Boynton', 'TJ BRENNAN': 'TJ Brennan', 'DANIEL BRIERE': 'Danny Briere',
         'TJ BRODIE': 'TJ Brodie', 'J.T. BROWN': 'JT Brown', 'ALEXANDRE BURROWS': 'Alex Burrows',
         'MICHAEL CAMMALLERI': 'Mike Cammalleri', 'DANIEL CARCILLO': 'Dan Carcillo', 'MATTHEW CARLE': 'Matt Carle',
         'DANNY CLEARY': 'Dan Cleary', 'JOSEPH CORVO': 'Joe Corvo', 'JOSEPH CRABB': 'Joey Crabb',
         'BJ CROMBEEN': 'BJ Crombeen', 'B.J. Crombeen': 'BJ Crombeen', 'EVGENII DADONOV': 'Evgeny Dadonov',
         'JACOB DE LA ROSE': 'Jacob de la Rose', 'JOE DIPENTA': 'Joe DiPenta', 'JON DISALVATORE': 'Jon DiSalvatore',
         'JACOB DOWELL': 'Jake Dowell', 'NICHOLAS DRAZENOVIC': 'Nick Drazenovic', 'ROBERT EARL': 'Robbie Earl',
         'ALEXANDER FROLOV': 'Alex Frolov', 'T.J. GALIARDI': 'TJ Galiardi', 'TJ GALIARDI': 'TJ Galiardi',
         'ANDREW GREENE': 'Andy Greene', 'MICHAEL GRIER': 'Mike Grier', 'NATHAN GUENIN': 'Nate Guenin',
         'MARTY HAVLAT': 'Martin Havlat', 'JOSHUA HENNESSY': 'Josh Hennessy', 'T.J. HENSICK': 'TJ Hensick',
         'TJ Hensick': 'TJ Hensick', 'CHRISTOPHER HIGGINS': 'Chris Higgins', 'ROBERT HOLIK': 'Bobby Holik',
         'MATTHEW IRWIN': 'Matt Irwin', 'P. J. AXELSSON': 'PJ Axelsson', 'PER JOHAN AXELSSON': 'PJ Axelsson',
         'JONATHON KALINSKI': 'Jon Kalinski', 'ALEXANDER KHOKHLACHEV': 'Alex Khokhlachev', 'DJ KING': 'DJ King',
         'Dwayne KING': 'DJ King', 'MICHAEL KNUBLE': 'Mike Knuble', 'KRYSTOFER KOLANOS': 'Krys Kolanos',
         'MICHAEL KOMISAREK': 'Mike Komisarek', 'STAFFAN KRONVALL': 'Staffan Kronwall',
         'NIKOLAY KULEMIN': 'Nikolai Kulemin', 'CLARKE MACARTHUR': 'Clarke MacArthur',
         'LANE MACDERMID': 'Lane MacDermid', 'ANDREW MACDONALD': 'Andrew MacDonald', 'RAYMOND MACIAS': 'Ray Macias',
         'CRAIG MACDONALD': 'Craig MacDonald', 'STEVE MACINTYRE': 'Steve MacIntyre', 'MAKSIM MAYOROV': 'Maxim Mayorov',
         'AARON MACKENZIE': 'Aaron MacKenzie', 'DEREK MACKENZIE': 'Derek MacKenzie', 'RODNEY PELLEY': 'Rod Pelley',
         'BRETT MACLEAN': 'Brett MacLean', 'ANDREW MACWILLIAM': 'Andrew MacWilliam', 'BRYAN MCCABE': 'Bryan McCabe',
         'OLIVIER MAGNAN': 'Olivier Magnan-Grenier', 'DEAN MCAMMOND': 'Dean McAmmond',
         'KENNDAL MCARDLE': 'Kenndal McArdle', 'ANDY MCDONALD': 'Andy McDonald', 'COLIN MCDONALD': 'Colin McDonald',
         'JOHN MCCARTHY': 'John McCarthy', 'STEVE MCCARTHY': 'Steve McCarthy', 'DARREN MCCARTY': 'Darren McCarty',
         'JAY MCCLEMENT': 'Jay McClement', 'CODY MCCORMICK': 'Cody McCormick', 'MAX MCCORMICK': 'Max McCormick',
         'BROCK MCGINN': 'Brock McGinn', 'TYE MCGINN': 'Tye McGinn', 'BRIAN MCGRATTAN': 'Brian McGrattan',
         'DAVID MCINTYRE': 'David McIntyre', 'NATHAN MCIVER': 'Nathan McIver', 'JAY MCKEE': 'Jay McKee',
         'CURTIS MCKENZIE': 'Curtis McKenzie', 'FRAZER MCLAREN': 'Frazer McLaren', 'BRETT MCLEAN': 'Brett McLean',
         'BRANDON MCMILLAN': 'Brandon McMillan', 'CARSON MCMILLAN': 'Carson McMillan', 'PHILIP MCRAE': 'Philip McRae',
         'FREDERICK MEYER IV': 'Freddy Meyer', 'MICHAEL MODANO': 'Mike Modano', 'CHRISTOPHER NEIL': 'Chris Neil',
         'MATTHEW NIETO': 'Matt Nieto', 'JOHN ODUYA': 'Johnny Oduya', 'PIERRE PARENTEAU': 'Pierre Parenteau',
         'MARC POULIOT': 'Marc-Antoine Pouliot', 'MAXWELL REINHART': 'Max Reinhart', 'MICHAEL RUPP': 'Mike Rupp',
         'ROBERT SCUDERI': 'Rob Scuderi', 'TOMMY SESTITO': 'Tom Sestito', 'MICHAEL SILLINGER': 'Mike Sillinger',
         'JONATHAN SIM': 'Jon Sim', 'MARTIN ST LOUIS': 'Martin St. Louis', 'MATTHEW STAJAN': 'Matt Stajan',
         'ZACHERY STORTINI': 'Zack Stortini', 'PK SUBBAN': 'PK Subban', 'WILLIAM THOMAS': 'Bill Thomas',
         'R.J. UMBERGER': 'RJ Umberger', 'RJ UMBERGER': 'RJ Umberger', 'MARK VAN GUILDER': 'Mark van Guilder',
         'BRYCE VAN BRABANT': 'Bryce van Brabant', 'DAVID VAN DER GULIK': 'David van der Gulik',
         'MIKE VAN RYN': 'Mike van Ryn', 'ANDREW WOZNIEWSKI': 'Andy Wozniewski', 'JAMES WYMAN': 'JT Wyman',
         'JT WYMAN': 'JT Wyman', 'NIKOLAY ZHERDEV': 'Nikolai Zherdev', 'HARRISON ZOLNIERCZYK': 'Harry Zolnierczyk',
         'MARTIN ST PIERRE': 'Martin St. Pierre', 'DENIS GAUTHIER JR.': 'Denis Gauthier Jr.',
         'MARC-ANDRE FLEURY': 'Marc-Andre Fleury', 'DAN LACOUTURE': 'Dan LaCouture', 'RICK DIPIETRO': 'Rick DiPietro',
         'JOEY MACDONALD': 'Joey MacDonald', 'B.J CROMBEEN': 'BJ Crombeen', 'TIMOTHY JR. THOMAS': 'Tim Thomas'}
CURRENT_TEAMS = ['CAR', 'WSH', 'T.B', 'WPG', 'FLA', 'NYR', 'NYI', 'PHI', 'PIT', 'N.J', 'BOS', 'MTL', 'BUF', 'TOR', 'OTT',
                 'DET', 'CHI', 'STL', 'NSH', 'CBJ', 'MIN', 'COL', 'VAN', 'CGY', 'EDM', 'ANA', 'S.J', 'L.A', 'ARI', 'DAL']

ESPN_DATE = ''
CURRENT_ESPN_URLS = {}
PREV_GAME_SEARCH = None
PREV_GAME_SEARCH_GAMES = None


def get_gamesheet_folder(season):
    """Returns the folder where the raw PBP/TOI files from the given season's games are stored.

    season: e.g. 2013 for 2013-14"""

    return '/Users/muneebalam/Desktop/NHLPlaybyPlay/Archive/{0:d}{1:d}/'.format(season, season + 1)


def get_parsed_gamesheet_folder(season):
    """Returns the folder where the parsed PBP/TOI files from the given season's games are stored.

    season: e.g. 2013 for 2013-14"""

    return '/Users/muneebalam/Desktop/NHLPlaybyPlay/Parsed/{0:d}{1:d}/'.format(season, season + 1)

def get_additional_data_folder():
    """Returns the folder where additional data files are stored"""

    return '/Users/muneebalam/Desktop/NHLPlaybyPlay/Parsed/Misc files/'


def get_pbp_filename(season, game):
    """Returns the *full* filename for raw PBP for the given game from given season.

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return '{0:s}{1:d} PBP.html'.format(get_gamesheet_folder(season), game)


def get_json_filename(season, game):
    """Returns the *full* filename for raw json for the given game from given season.

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return '{0:s}{1:d} JSON.json'.format(get_gamesheet_folder(season), game)


def get_toih_filename(season, game):
    """Returns the *full* filename for raw TOI for the given game from given season, for home team.

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return '{0:s}{1:d} TOIH.html'.format(get_gamesheet_folder(season), game)


def get_toiv_filename(season, game):
    """Returns the *full* filename for raw TOI for the given game from given season, for road team.

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return '{0:s}{1:d} TOIV.html'.format(get_gamesheet_folder(season), game)


def get_parsed_toimatrix_filename(season, game):
    """Returns the *full* filename for TOI matrix for the given game from given season.

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return '{0:s}{1:d} TOIM.csv'.format(get_parsed_gamesheet_folder(season), game)


def get_parsed_pbp_filename(season, game):
    """Returns the *full* filename for parsed PBP for the given game from given season.

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return '{0:s}{1:d} PBP.csv'.format(get_parsed_gamesheet_folder(season), game)


def get_parsed_toih_filename(season, game):
    """Returns the *full* filename for raw TOI for the given game from given season, for home team.

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return '{0:s}{1:d} TOIH.csv'.format(get_parsed_gamesheet_folder(season), game)


def get_parsed_toiv_filename(season, game):
    """Returns the *full* filename for raw TOI for the given game from given season, for road team.

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return '{0:s}{1:d} TOIV.csv'.format(get_parsed_gamesheet_folder(season), game)


def get_pbp_url(season, game):
    """Returns NHL.com URL for PBP for given game

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return 'http://www.nhl.com/scores/htmlreports/{0:d}{1:d}/PL0{2:d}.HTM'.format(season, season + 1, game)


def get_json_url(season, game):
    """Returns NHL.com URL for JSON for given game

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return 'http://live.nhl.com/GameData/{0:d}{1:d}/{0:d}0{2:d}/PlayByPlay.json'.format(season, season + 1, game)


def get_summary_url(season, game):
    """Returns NHL.com URL for JSON summary for given game

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return 'http://live.nhl.com/GameData/{0:d}{1:d}/{0:d}0{2:d}/Summary.json'.format(season, season + 1, game)


def get_toih_url(season, game):
    """Returns NHL.com URL for home TOI for given game

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return 'http://www.nhl.com/scores/htmlreports/{0:d}{1:d}/TH0{2:d}.HTM'.format(season, season + 1, game)


def get_toiv_url(season, game):
    """Returns NHL.com URL for road TOI for given game

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return 'http://www.nhl.com/scores/htmlreports/{0:d}{1:d}/TV0{2:d}.HTM'.format(season, season + 1, game)

"""
def get_espn_date_url(d):
    #http://espn.go.com/nhl/scoreboard?date=20070913
    #as Sep 13 2007; just add days

    from datetime import date
    start = date(2007, 9, 13)
    i = d.rindex(',')
    month = d[d.index(',')+2:i-2].strip()
    month = MONTHS[month]
    year = int(d[i+2:])
    day = int(d[i-2:i].strip())
    end = date(year, month, day)
    diff = str((end - start).days + 913)
    diff = (4 - len(diff))*'0'+diff
    print('{0:s}-->{1:s}'.format(d, diff))
    return "http://espn.go.com/nhl/scoreboard?date=2007{0:s}".format(diff)


def update_espn_date_game_urls(date):
    #Returns ESPN URL for PBP for given game.
    #season: e.g. 2013 for 2013-14
    #game: five-digit number format (from 20001 to 21230 for regular season)
    global ESPN_DATE
    global CURRENT_ESPN_URLS
    if not date == ESPN_DATE:
        CURRENT_ESPN_URLS = {}
        ESPN_DATE = date
        import urllib.request
        url = get_espn_date_url(date)
        r = urllib.request.urlopen(url)
        page = r.read().decode('utf-8')
        r.close()
        indic = '/nhl/recap?gameId='
        base = 'http://sports.espn.go.com/nhl/gamecast/data/masterFeed?lang=en&isAll=true&gameId='
        while True:
            try:
                page = page[page.index(indic) + len(indic):]
                gamenum = page[:9]
                teams = page[page.index('>')+1:page.index('<')]
                teams = teams.split(',')
                road = teams[0][:teams[0].rindex(' ')].strip()
                home = teams[1][:teams[1].rindex(' ')].strip()
                gameurl = '{0:s}{1:s}'.format(base, gamenum)
                CURRENT_ESPN_URLS['{0:s}@{1:s}'.format(road, home)] = gameurl
                CURRENT_ESPN_URLS['{0:s}@{1:s}'.format(home, road)] = gameurl
            except ValueError:
                print(str(CURRENT_ESPN_URLS))
                break
    return CURRENT_ESPN_URLS

def get_espn_game_url(date, road, home):
    urls = update_espn_date_game_urls(date)
    key = '{0:s}@{1:s}'.format(MASCOT_NAMES[road], MASCOT_NAMES[home])
    if key not in urls:
        pass
    return urls[key]
"""

def get_espn_filename(season, game):
    return '{0:s}{1:d} ESPN.html'.format(get_gamesheet_folder(season), game)


def get_team_pbplog_filename(season, team):
    """Returns the *full* filename for the pbp log for the given team from given season.

    season: e.g. 2013 for 2013-14
    team: three-letter abbrev (from 20001 to 21230 for regular season)"""

    return '{0:s}{1:s} PBP log.csv'.format(get_parsed_gamesheet_folder(season), team)


def get_team_toilog_filename(season, team):
    """Returns the *full* filename for the toi log for the given team from given season.

    season: e.g. 2013 for 2013-14
    team: three-letter abbrev (from 20001 to 21230 for regular season)"""

    return '{0:s}{1:s} TOI log.csv'.format(get_parsed_gamesheet_folder(season), team)

"""
def save_espn(season, game, date, home, road):
    try:
        url = get_espn_game_url(date, home, road)
    except KeyError:
        print('Could not find gamecast for {0:s}@{1:s} in {2:d} {3:d} {4:s}'.format(road, home, season, game, date))
        return
    fname = get_espn_filename(season, game)
    import urllib.request
    try:
        #print(url)
        r = urllib.request.urlopen(url)
        data = r.read().decode('utf-8')
        r.close()

        w = open(fname, 'w')
        w.write(data)
        w.close()
    except urllib.request.HTTPError:
        print('Issue accessing', url)
"""

def save(season, gamelist, force_overwrite=False):
    """Saves PBP, JSON, and TOI logs (unformatted) to gamesheet folder

    season: e.g. 2013 for 2013-14"""
    for game in gamelist:
        filename_pbp = get_pbp_filename(season, game)
        url_pbp = get_pbp_url(season, game)
        filename_json = get_json_filename(season, game)
        url_json = get_json_url(season, game)
        filename_toih = get_toih_filename(season, game)
        url_toih = get_toih_url(season, game)
        filename_toiv = get_toiv_filename(season, game)
        url_toiv = get_toiv_url(season, game)

        dct = {url_pbp: filename_pbp, url_json: filename_json, url_toih: filename_toih, url_toiv: filename_toiv}

        for key in dct:
            if force_overwrite or not os.path.isfile(dct[key]):
                try:
                    save_file(key, dct[key])
                except urllib.request.URLError:
                    print('URL not found: {0:s}'.format(key))
                except KeyboardInterrupt:
                    save_file(key, dct[key])
                    break
        print('Done with {0:d} {1:d}'.format(season, game))


def get_season_saved_gamelist(season, seg=['regular', 'playoff'], team1=None, team2=None):
    """Gets all games from season. Use regular, playoff, preseason, all-star, and/or olympics for seg.
    Picks one team from both team1 and team2"""
    if isinstance(seg, str):
        seg = [seg]
    if isinstance(team1, str):
        team1 = [team1]
    if isinstance(team2, str):
        team2 = [team2]
    segs = set()
    for i in range(len(seg)):
        segs.add(seg[i])

    if PREV_GAME_SEARCH is not None and (season, segs) == PREV_GAME_SEARCH:
        pass
    else:
        PREV_GAME_SEARCH_GAMES = {}
        base = get_parsed_gamesheet_folder(season)
        filelst = os.listdir(base)
        if '.DS_Store' in filelst:
            filelst.remove('.DS_Store')
        gameset = set()
        game_id_dct = {1: 'preseason', 2: 'regular', 3: 'playoff', 4: 'all-star', 9: 'olympics'}
        for file in filelst:
            try:
                gamenum = int(file[:5])
                if gamenum not in PREV_GAME_SEARCH_GAMES:
                    if gamenum // 10000 not in game_id_dct:
                        pass
                    elif 'all' in segs or game_id_dct[gamenum // 10000] in segs:
                        try:
                            r = open(get_parsed_pbp_filename(season, gamenum), 'r')
                            line = r.readline()
                            r.close()
                            try:
                                line = line[line.index(':') + 1:].strip().split('@')
                                teams = [TEAM_MAP[line[0]], TEAM_MAP[line[1]]]
                                PREV_GAME_SEARCH_GAMES[gamenum] = teams
                            except ValueError:
                                print('Could not get home/road for {0:d} {1:d}'.format(season, gamenum))
                                print(line)
                        except FileNotFoundError:
                            print('Parsed PBP file not found for', season, gamenum)
            except ValueError:
                pass

    gameset = set()
    for game, (t1, t2) in PREV_GAME_SEARCH_GAMES.items():
        if (team1 is None or team1 == t1 or team1 == t2) and (team2 is None or team2 == t1 or team2 == t2):
            gameset.add(game)
    gameset = list(gameset)
    gameset.sort()
    return gameset


def save_file(url, savefile):
    """Reads given url and saves as given savefile"""
    try:
        reader = urllib.request.urlopen(url)
        data = reader.read().decode('utf-8')
        reader.close()
    except http.client.IncompleteRead:
        print('Did not finish reading {0:s}; re-run to grab it later'.format(url))
        return

    writer = open(savefile, 'w')
    writer.write(data)
    writer.close()
    time.sleep(1)


def gamepages(season, force_overwrite=False):
    """Parses raw files saved from Internet into csvs, which are saved in parsed gamesheet folder

    season: e.g. 2013 for 2013-14"""

    gamelist = get_season_gamelist(season)
    save(season, gamelist, force_overwrite)

    for game in gamelist:
        try:
            parse_game(season, game, force_overwrite)
            print('Done with {0:d} {1:d}'.format(season, game))
        except Exception as e:
            print(season, game, e)


def parse_game(season, game, force_overwrite=False):
    """Intermediate method--parses PBP/TOIH/TOIV"""

    roster_dct = {} #{MTL: {#14 Plekanec: Tomas Plekanec}}
    try:
        hname, hdct = parse_toih(season, game, force_overwrite) #turns the TOIH HTML into parsed TOIH csv
        roster_dct[TEAM_MAP[hname]] = hdct
    except FileNotFoundError:
        print('No TOIH for', season, game)

    try:
        rname, rdct = parse_toiv(season, game, force_overwrite) #turns the TOIV HTML into parsed TOIV csv
        roster_dct[TEAM_MAP[rname]] = rdct
    except FileNotFoundError:
        print('No TOIV for', season, game)

    try:
        parse_pbp(season, game, force_overwrite, player_short_to_long=roster_dct) #turns the PBP and JSON HTML into parsed PBP csv
    except FileNotFoundError:
        print('No PBP for', season, game)

    try:
        save_toimatrix(season, game, force_overwrite) #turns the TOIH and TOIV HTML into a toi matrix
    except FileNotFoundError:
        print('Could not make toimatrix for', season, game)

def parse_pbp(season, game, force_overwrite=False, espn=True, player_short_to_long=None):
    """Checks if PBP file needs parsing. If it does (or if force_overwrite=True), parses it. Also saves ESPN"""
    import os
    folder = get_parsed_gamesheet_folder(season)
    if not os.path.exists(folder):
        os.makedirs(folder) #creates parsed gamesheet folder if it does not exist
    fname = get_parsed_pbp_filename(season, game)
    if force_overwrite or not os.path.isfile(fname):
        try:
            r = open(get_pbp_filename(season, game), 'r') #opens a reader for the PBP HTML
            data = r.read()
            r.close()

            data = data[data.index('VISITOR'):]
            data = strip_out_html(data)
            data = onelist(data)

            breakpt = search_list(data, '#', 0)

            basicinfo = data[:breakpt]
            data = data[breakpt:]

            homename, roadname = get_team_names(basicinfo)
            hshort = TEAM_MAP[homename]
            rshort = TEAM_MAP[roadname]
            date = get_game_date(basicinfo)
            if espn:
                pass#save_espn(season, game, date, homename, roadname)

            starttime, endtime = get_start_end_times(basicinfo)
            attendance, venue = get_attendance_venue(basicinfo)
            xy = read_event_locations(season, game, TEAM_MAP[homename], TEAM_MAP[roadname])

            events = read_events(data, xy, TEAM_MAP[homename], TEAM_MAP[roadname])

            if player_short_to_long is not None and len(player_short_to_long) > 1:
                for i in range(len(events)):
                    try:
                        if not events[i][8] == 'n/a':
                            if not events[i][8][0] == '#':
                                events[i][8] = '#' + events[i][8]
                            events[i][8] = player_short_to_long[events[i][6]][events[i][8].upper()]

                        if not events[i][9] == 'n/a':
                            if not events[i][9][0] == '#':
                                events[i][9] = '#' + events[i][8]
                            if events[i][6] == hshort:
                                events[i][9] = player_short_to_long[rshort][events[i][9].upper()]
                            else:
                                events[i][9] = player_short_to_long[hshort][events[i][9].upper()]
                    except KeyError:
                        if events[i][8] == 'Team':
                            pass
                        elif events[i][8] == '#':
                            events[i][8] = 'n/a'
                        elif events[i][9] == '#':
                            events[i][9] = 'n/a'
                        else:
                            print(events[i])

            flipxy = [] #some JSON have home shooting left first, others home shooting right. Want the latter
            for i in range(len(events)):
                if 'n/a' not in events[i][11]:
                    x = int(events[i][11][1:events[i][11].index(';')])
                    if int(events[i][1]) % 2 == 1: #OZ events at x > 0, otherwise x < 0
                        if events[i][7] == 'Off':
                            if x > 0:
                                flipxy.append(False)
                            else:
                                flipxy.append(True)
                        elif events[i][7] == 'Def':
                            if x > 0:
                                flipxy.append(True)
                            else:
                                flipxy.append(False)
                    else:
                        if events[i][7] == 'Def':
                            if x > 0:
                                flipxy.append(False)
                            else:
                                flipxy.append(True)
                        elif events[i][7] == 'Off':
                            if x > 0:
                                flipxy.append(True)
                            else:
                                flipxy.append(False)

            flipxy = sum(flipxy) > len(flipxy) / 10 #allowing  up to 10% of shots to come from opp zone
            if flipxy:
                for i in range(len(events)):
                    if 'n/a' not in events[i][11]:
                        x = int(events[i][11][1:events[i][11].index(';')])
                        y = int(events[i][11][events[i][11].index(';') + 1:-1])
                        events[i][11] = '({0:d};{1:d})'.format(x * -1, y * -1)

            w = open(fname, 'w')
            w.write('Game {0:d}: {1:s}@{2:s}\n{3:s}\nStart {4:s} End {5:s}'.format(game, roadname, homename, date,
                                                                                   starttime, endtime))
            w.write('\nAttendance {0:s}\n{1:s}'.format(attendance, venue))
            w.write('\n#,Period,Strength,Time,Score,Event,Team,Zone,Actor,Recipient,Note,XY')
            w.write(',Home on ice,Road on ice')
            for i in range(len(events)):
                w.write('\n{0:s}'.format(','.join([str(x) for x in events[i]])))
            w.close()

        except FileNotFoundError as fnfe:
            if game <= 21230:
                print('Could not find {0:s}'.format(get_pbp_filename(season, game)))
        except ValueError as ve:
            if season == 2011 and game == 20259:
                pass
            else:
                print('Value error in', season, game, ve, ve.args)


def onelist(info):
    """Converts nested lists of lists of lists of strings into single list of strings"""
    lst = []
    for i in range(len(info)):
        if isinstance(info[i], str):
            lst.append(info[i])
        else:
            for j in range(len(info[i])):
                if isinstance(info[i][j], str):
                    lst.append(info[i][j])
                else:
                    for k in range(len(info[i][j])):
                        if isinstance(info[i][j][k], str):
                            lst.append(info[i][j][k])
                        else:
                            print('too many layers')
                            lst.append(info[i][j][k])
    return lst

def read_event_locations(season, game, hname, rname):
    """Returns a dct of {event time: (x,y)}"""

    event_dct = {}
    try:
        import json
        r = open(get_json_filename(season, game), 'r')
        data = r.read()
        r.close()
        json_dct = json.loads(data)
        pbp = json_dct['data']['game']['plays']['play']
        for id in range(len(pbp)):
            evtype = pbp[id]['type'].upper()
            if evtype == 'PENALTY':
                evtype = 'PENL'
            evtime = convert_time(pbp[id]['time'], pbp[id]['period'])
            try:
                xy = '({0:d};{1:d})'.format(pbp[id]['xcoord'], pbp[id]['ycoord'])
            except KeyError:
                #print([key for key in pbp[id]])
                xy = '(n/a;n/a)'
            event_dct['{0:s} {1:d}'.format(evtype, evtime)] = xy
    except FileNotFoundError:
        print('No JSON for', season, game)

    try:
        r = open(get_espn_filename(season, game), 'r')
        data = r.read()
        r.close()

        data = data[data.index('<Plays>')+7:data.index('</Plays>')-8].split('</Play>')
        playtypes = {'Stoppage': 'STOP', 'faceoff': 'FAC', 'Shot missed': 'MISS', 'Penalty': 'PENL',
                     'Shot on goal': 'SHOT', 'Shot blocked': 'BLOCK', 'Takeaway': 'TAKE',
                     'Giveaway': 'GIVE', 'Goal scored': 'GOAL'}
        for i in range(len(data)):
            line = data[i].split('~')

            evtype = None
            for play in playtypes:
                if play in line[8]:
                    evtype = playtypes[play]
                    break
            if evtype is None:
                #print(str(data[i]))
                #print(line[8])
                evtype = ''
            else:
                evtime = convert_time(line[3], int(line[4]))
                x = int(line[0][line[0].rindex('[') + 1:])
                y = int(line[1])
                event_dct['{0:s} {1:d}'.format(evtype, evtime)] = '({0:d};{1:d})'.format(x, y)
    except FileNotFoundError:
        print('No ESPN for', season, game)

    return event_dct

def read_events(gamedata, xy, hname, rname):
    """Reads and formats PBP from a game"""
    event_is = []
    event_id = 1
    while True:
        event_id = search_list(gamedata, EVENT_TYPES, event_id + 1)
        if event_id == 0:
            break
        event_is.append(event_id)
    eventlst = []
    hscore = 0
    rscore = 0
    hplayermap = {}
    rplayermap = {} # actor/recip are formatted as #num lastname, want to make them full names
    for i in range(len(event_is)):
        evtype = gamedata[event_is[i]]
        start = event_is[i] + EVENT_HELPER[evtype]
        if i < len(event_is) - 1:
            end = event_is[i + 1] - 3
        else:
            end = len(gamedata)
        rel_data = gamedata[start:end]
        try:
            evnumber = int(rel_data[0])
            period = int(rel_data[1])
        except ValueError:
            try:
                rel_data = rel_data[1:]
                evnumber = int(rel_data[0])
                period = int(rel_data[1])
            except ValueError:
                #for 2014 20971, game started 1-0 carryover from Peverley collapse
                evnumber = 0
                period = 1
                team = 'CBJ'
                actor = '#8 Horton'
                recip = 'n/a'
                zone = 'Off'
                note = 'Assists: #11 CALVERT; #21 WISNIEWSKI'
                strength = '0v0'
                time = '0:00'
                event_xy = '(n/a;n/a)'
                timeonly = '0'

                rel_data = rel_data[3:]
        if not period == 0:
            if ':' in rel_data[3]:
                time = rel_data[3]
            else:
                time = rel_data[2]
            time = time[:time.index(' ')]
            team, zone, actor, recip, note = get_team_zone_player_recipient_note(gamedata[event_is[i]:event_is[i] + 2], hname, rname)
            if team == rname or evtype == 'BLOCK' and not team == hname:
                if zone == 'Off':
                    zone = 'Def'
                elif zone == 'Def':
                    zone = 'Off'
            hplayers = []
            rplayers = []
            player_starti = len(rel_data)
            for i in range(len(rel_data)):
                if '-' in rel_data[i]:
                    if rel_data[i].split('-')[0].strip() in POSITIONS2:
                        player_starti = i
                        break
            hr_breaki = len(rel_data)
            for i in range(player_starti, len(rel_data)):
                if '-' in rel_data[i]:
                    if rel_data[i].split('-')[0].strip() in POSITIONS2:
                        if len(rel_data[i - 1]) == len(rel_data[i + 1]) == 1:
                            hr_breaki = i
                            break
            player_endi = len(rel_data)
            for i in range(len(rel_data)):
                if 'Copyright' in rel_data[i] or 'VISITOR' in rel_data[i]:
                    player_endi = i
                    break
            hgoalie = False
            rgoalie = False
            for i in range(player_starti, player_endi):
                if rel_data[i] in POSITIONS:
                    if i < hr_breaki:
                        rplayers[-1] = rel_data[i] + ' ' + rplayers[-1]
                        if rel_data[i] == 'G':
                            rgoalie = True
                    else:
                        hplayers[-1] = rel_data[i] + ' ' + hplayers[-1]
                        if rel_data[i] == 'G':
                            hgoalie = True
                elif len(rel_data[i]) > 4:
                    if i < hr_breaki:
                        rplayers.append(fixname('-'.join(rel_data[i].split('-')[1:]).strip()))
                    else:
                        hplayers.append(fixname('-'.join(rel_data[i].split('-')[1:]).strip()))
            event_xy = '(n/a;n/a)'
            try:
                timeonly = str(convert_time(time, period))
            except ValueError:
                if evnumber == 351 and evtype == 'PEND' and hname == 'NYI' and rname == 'BUF':
                    timeonly = '3900'
            eventkey = '{0:s} {1:s}'.format(evtype, timeonly)
            if eventkey in xy:
                event_xy = xy[eventkey]
            else:
                if timeonly in xy:
                    event_xy = xy[timeonly]
            if hgoalie and rgoalie:
                strength = '{0:d}v{1:d}'.format(len(hplayers) - 1, len(rplayers) - 1)
            elif not hgoalie and not rgoalie:
                strength = '{0:d}+1v{1:d}+1'.format(len(hplayers) - 1, len(rplayers) - 1)
            elif not hgoalie:
                strength = '{0:d}+1v{1:d}'.format(len(hplayers) - 1, len(rplayers) - 1)
            elif not rgoalie:
                strength = '{0:d}v{1:d}+1'.format(len(hplayers) - 1, len(rplayers) - 1)
            else:
                print('what strength?', rel_data)

        score = '{0:d}-{1:d}'.format(hscore, rscore)
        eventlst.append([evnumber, str(period), strength, time, score, evtype, team, zone, actor, recip, note, event_xy,
                         ';'.join(hplayers), ';'.join(rplayers)])
        #print(eventlst[-1])
        for p in hplayers:
            pos, fn, ln = p.split(' ', 2)
            hplayermap[ln.lower()] = fn + ' ' + ln
        for p in rplayers:
            pos, fn, ln = p.split(' ', 2)
            rplayermap[ln.lower()] = fn + ' ' + ln
        if evtype == 'GOAL':
            if team == hname:
                hscore += 1
            elif team == rname:
                rscore += 1
            else:
                print('which team?', rel_data)
    return eventlst


def get_team_zone_player_recipient_note(evdata, hname, rname):
    """For even data, returns acting team, zone of event, acting player, recipient player, and any notes"""
    team = 'n/a'
    note = 'n/a'
    zone = 'n/a'
    actor = 'n/a'
    recip = 'n/a'
    evdata[1] = evdata[1].replace(',', '')
    #print(evdata)
    if evdata[1][:8] == 'PHI #48 ':
        pass
    if evdata[0] == 'PSTR':
        string = evdata[1][evdata[1].index('Period Start') + 14:].strip()
        note = string[string.index(':') + 1:].strip()
    elif evdata[0] == 'PEND':
        note = evdata[1].split('-')[1].strip()
        note = note[note.index(':') + 1:].strip()
    elif evdata[0] == 'GEND':
        note = evdata[1].split('-')[1].strip()
        note = note[note.index(':') + 1:].strip()
    elif evdata[0] == 'FAC':
        strings = [s.strip() for s in evdata[1].split('-')]
        if len(strings) > 2:
            strings = [strings[0], '-'.join(strings[1:])]
        team = strings[0][:3]
        try:
            zone = strings[0].split(' ')[2]
        except IndexError:
            print('fixing zone for', strings)
            zone = strings[0].split(' ')[0]
            team = 'n/a'
        hi = strings[1].index(hname)
        ri = strings[1].index(rname)
        if team == hname and ri < hi or team == rname and hi < ri:
            recip, actor = tuple([s.strip()[4:] for s in strings[1].split('vs')])
        elif team == hname and hi < ri or team == rname and ri < hi:
            actor, recip = tuple([s.strip()[4:] for s in strings[1].split('vs')])
    elif evdata[0] == 'HIT':
        try:
            i = evdata[1].index(' Zone')
            zone = evdata[1][i - 5:i].strip()
        except (IndexError, ValueError):
            pass
        strings = evdata[1].split(' ')
        team = strings[0]
        actor = ' '.join(strings[1:3])
        recip = ' '.join(strings[5:7])
    elif evdata[0] == 'BLOCK':
        strings = evdata[1].split(' BLOCKED BY ')
        if strings[0] == '':
            strings = strings[1:]
        actor = strings[0].strip()
        team = actor[:3]
        actor = strings[0][4:]
        strings = strings[1].split(' ')
        zi = search_list(strings, ZONES, 0)
        zone = strings[zi]
        if strings[zi - 1].isupper():
            note = 'n/a'
            recip = ' '.join(strings[1:zi]).strip()
        else:
            note = strings[zi - 1]
            recip = ' '.join(strings[1:zi - 1]).strip()

        if recip[:3] in TEAMS:
            recip = recip[4:]
        if zone == 'Def.':
            zone = 'Off.'
        elif zone == 'Off.':
            zone = 'Def.'
    elif evdata[0] == 'SHOT':
        team = evdata[1][:3]
        evdata[1] = evdata[1].replace('Tip-In', 'Tip').replace('Tip in', 'Tip')
        strings = evdata[1].split('-', 1)[1].strip().split(' ')
        zi = search_list(strings, ZONES, 0)
        if strings[zi - 1].isupper():
            actor = ' '.join(strings[:zi])
            note = ' '.join(strings[-2:])
        else:
            actor = ' '.join(strings[:zi - 1])
            note = strings[zi - 1] + ' ' + ' '.join(strings[-2:])
        zone = strings[zi]
    elif evdata[0] == 'MISS':
        evdata[1] = evdata[1].replace('Tip-In', 'Tip').replace('Tip in', 'Tip')
        strings = evdata[1].split(' ')
        actor = ' '.join(strings[1:3])
        team = strings[0]
        zi = search_list(strings, ZONES, 0)
        zone = strings[zi]
        note = ' '.join(strings[3:zi]) + ' ' + ' '.join(strings[-2:])
        if strings[3] not in {'Snap', 'Backhand', 'Slap', 'Wrist', 'Tip', 'Tip-In', 'Wrap', 'Deflected', 'Wrap-around'}:
            if strings[3] in {'Over', 'Wide', 'Goalpost'}:
                note = 'n/a' + note
            elif strings[3] == 'JR.':
                actor = actor + ' ' + strings[3]
                note = note[note.index(' ') + 1:]
            elif strings[3] == zone:
                note = 'n/a n/a' + note
            elif strings[3] in {'LOUIS', 'III', 'PARENTEAU', 'RIEMSDYK', 'HAAN', 'VRIES', 'RYN', 'IV', 'PIERRE'}:
                actor = actor + ' ' + strings[3]
                note = note[note.index(' ') + 1:]
            elif strings[3] == 'Penalty':
                pass
            else:
                if strings[4] in {'Snap', 'Backhand', 'Slap', 'Wrist', 'Tip', 'Tip-In', 'Wrap', 'Deflected', 'Wrap-around'}:
                    actor = ' '.join(strings[1:4])
                    note = ' '.join(strings[4:zi]) + ' ' + ' '.join(strings[-2:])
                else:
                    if strings[5] in {'Snap', 'Backhand', 'Slap', 'Wrist', 'Tip', 'Tip-In', 'Wrap', 'Deflected', 'Wrap-around'}:
                        actor = ' '.join(strings[1:5])
                        note = ' '.join(strings[5:zi]) + ' ' + ' '.join(strings[-2:])
                    else:
                        print(evdata[1])
    elif evdata[0] == 'GOAL':
        team = evdata[1][:3]
        strings = evdata[1].split(' ')
        zi = search_list(strings, ZONES, 0)
        zone = strings[zi]
        note = strings[zi - 1] + ' ' + ' '.join(strings[zi + 2:])
        try:
            actor = evdata[1][3:evdata[1].index('(')].strip()
        except ValueError:
            actor = ' '.join(strings[1:zi - 1])
        while '(' in note:
            i1 = note.index('(')
            i2 = note.index(')')
            note = note[:i1] + note[i2 + 1:]
    elif evdata[0] == 'GIVE':
        team = evdata[1][:3]
        strings = '-'.join(evdata[1].split('-')[1:]).strip().split(' ')
        zi = search_list(strings, ZONES, 0)
        actor = ' '.join(strings[:zi])
        if actor == '':
            if '#' in evdata[1]:
                actor = evdata[1][evdata[1].index('#'):]
            else:
                actor = 'n/a'
        else:
            zone = strings[zi]
    elif evdata[0] == 'TAKE':
        team = evdata[1][:3]
        strings = '-'.join(evdata[1].split('-')[1:]).strip().split(' ')
        zi = search_list(strings, ZONES, 0)
        actor = ' '.join(strings[:zi])
        if actor == '':
            if '#' in evdata[1]:
                actor = evdata[1][evdata[1].index('#'):]
            else:
                actor = 'n/a'
        else:
            zone = strings[zi]
    elif evdata[0] == 'PENL':
        team = evdata[1][:3]
        strings = evdata[1].split(' ')
        zi = search_list(strings, ZONES, 0)
        note = evdata[1][4:evdata[1].index(')') + 1]
        if zi == 0:
            zi = len(strings)
        else:
            zone = strings[zi]
        pi = 0
        for i in range(zi):
            if strings[i].isupper() or len(strings[i]) > 0 and strings[i][0] == '#':
                pi = i + 1
            else:
                break
        actor = ' '.join(strings[1:pi])
        if actor in note:
            note = note[len(actor):].strip()
        if 'Drawn By' in evdata[1]:
            endi = evdata[1].index('Drawn By')
            recip = evdata[1][endi + 9:].strip()[4:]
            if 'Served By' in evdata[1]:
                if not zone == 'n/a':
                    endi = evdata[1].index(zone)
                servingname = evdata[1][evdata[1].index('Served By'):endi].strip().split('#')
                note += ' ' + servingname[0] + '#' + fixname(servingname[1])
        elif 'Served By' in evdata[1]:
            servingname = evdata[1][evdata[1].index('Served By'):].strip().split('#')
            note += ' ' + servingname[0] + '#' + fixname(servingname[1])
        if note[-5:] == ' Zone':
            note = note[:-9].strip()
        found = False
        for p in PENALTIES:
            if len(note) >= len(p) and p == note[:len(p)]:
                found = True
                note = fix_penalty(p) + note[len(p):]
                break
        if not found:
            print(team, zone, actor, recip, note)
            print(evdata[1])
        if team == 'Tea' or team == 'TEA':
            print('fixing', team, zone, actor, recip, note)
            team = 'n/a'
            actor = 'TEAM'
    elif evdata[0] == 'STOP':
        note = evdata[1]
        if 'TIMEOUT' in note:
            if 'TV TIMEOUT' in note:
                i = note.index('TV TIMEOUT')
                if not note[i - 1] == ' ':
                    note = note[:i] + ' ' + note[i:]
            elif 'VISITOR TIMEOUT' in note:
                i = note.index('VISITOR TIMEOUT')
                if not note[i - 1] == ' ':
                    note = note[:i] + ' ' + note[i:]
                team = rname
            elif 'HOME TIMEOUT' in note:
                i = note.index('HOME TIMEOUT')
                if not note[i - 1] == ' ':
                    note = note[:i] + ' ' + note[i:]
                team = hname
            else:
                i = note.index('TIMEOUT')
                if not note[i - 1] == ' ':
                    note = note[:i] + ' ' + note[i:]
        elif 'CHLG' in note:
            note = note.replace('CHLG', 'Challenge').replace('HM', 'Home').replace('RD', 'Road')
        if len(note) > 0:
            note = fixname(note)
    elif evdata[0] == 'EISTR':
        string = evdata[1][evdata[1].index('Early Intermission Start') + 26:].strip()
        note = string[string.index(':') + 1:].strip()
    elif evdata[0] == 'EIEND':
        string = evdata[1][evdata[1].index('Early Intermission End') + 24:].strip()
        note = string[string.index(':') + 1:].strip()
    elif evdata[0] == 'SOC':
        note = evdata[1][evdata[1].index('-') + 1:].strip()
    elif evdata[0] == 'GOFF':
        pass
    elif evdata[0] == 'CHL':
        note = evdata[1]
        team = note[:3]
        note = note[note.index('-') + 1:].strip()
    else:
        print('Could not ID event', evdata)
    if zone == '':
        zone = 'n/a'
    if zone[-1] == '.':
        zone = zone[:-1]
    return team, zone, fixname(actor), fixname(recip), note


def search_list(lst, items, start_i):
    """Searches list for any of items, beginning at start_i. Returns index of exact match, or 0"""
    if isinstance(items, str):
        items = [items]
    for i in range(start_i, len(lst)):
        if lst[i] in items:
            return i
    return 0


def get_team_names(gamedata):
    """Returns (homename, roadname)"""
    rname = None
    hname = None
    for i in range(len(gamedata)):
        if 'Game' in gamedata[i]:
            rname = gamedata[i][:gamedata[i].index('Game')].strip()
            break
    for i in range(len(gamedata) - 1, 0, -1):
        if 'Game' in gamedata[i]:
            hname = gamedata[i][:gamedata[i].index('Game')].strip()
            break
    hname = ' '.join([x for x in hname.split(' ') if x.isupper()])
    rname = ' '.join([x for x in rname.split(' ') if x.isupper()])
    return hname, rname


def get_game_date(gamedata):
    """Parse game data"""
    for i in range(len(gamedata)):
        if len(gamedata[i]) >= 3 and gamedata[i][:3] in DAYS_SHORT:
            return gamedata[i]
    return 'Date n/a'


def get_start_end_times(gamedata):
    """Parse game start and end times"""
    for i in range(len(gamedata)):
        if len(gamedata[i]) >= 5 and gamedata[i][:5] == 'Start':
            st = gamedata[i].replace('Start', '')
            st = st.replace('End', '')
            lst = [x.strip() for x in st.split(';')]
            if len(lst) == 2:
                return lst
            else:
                print(str(lst))
                print(str(gamedata[i]))
                return [lst[0], 'n/a']
    return ['n/a', 'n/a']


def get_attendance_venue(gamedata):
    """Parse attendance and venue"""
    for i in range(len(gamedata)):
        if gamedata[i][:10] == 'Attendance':
            lst = [x.strip() for x in gamedata[i][10:].strip().split('at')]
            lst[0] = lst[0].replace(',', '')
            if len(lst) == 3:
                return [lst[0], lst[1] + 'at' + lst[2]]
            elif len(lst) == 1:
                print(str(lst))
                return [lst[0], 'n/a']
            else:
                return lst
    return ['n/a', 'n/a']


def parse_toih(season, game, force_overwrite=False):
    """Checks if TOIH file needs parsing. If it does (or if force_overwrite=True), parses it.
    returns (teamname, {# name: full name})"""

    fname = get_toih_filename(season, game)
    parsed_fname = get_parsed_toih_filename(season, game)
    hdict = {}
    hname = ''
    if force_overwrite or not os.path.isfile(parsed_fname):
        r = open(fname, 'r')
        data = r.read()
        r.close()

        data = data[data.index('img src') + 1:]
        rname = data[data.index('alt'):data.index('>')]
        rname = rname.split('"')[1]

        data = data[data.index('img src') + 1:]
        data = data[data.index('img src') + 1:]
        data = data[data.index('img src') + 1:]
        hname = data[data.index('alt'):data.index('>')]
        hname = hname.split('"')[1]

        data = data[data.index(hname) + 1:]
        data = data[data.index(hname) + 1:]

        data2 = data.split('playerHeading')

        shift_data_startend = {}
        player_order = []

        for i in range(1, len(data2)):
            name = data2[i][data2[i].index('>') + 1:data2[i].index('<')]
            name_short = '#' + name[:name.index(',')]
            namei = name.index(' ')
            name = name[:namei] + ' ' + fixname(name[namei + 1:])
            hdict[name_short.upper()] = name[2:].strip()
            line = data2[i][data2[i].index('Start of Shift') + 1:]
            line = line[:line.index('Per')].split('>')
            shift_data_startend[name] = []
            player_order.append(name)
            for j in range(16, len(line), 14):
                j2 = j
                try:
                    shiftnum = int(line[j2][:line[j2].index('<')])
                except ValueError:
                    j2 = j + 1
                    try:
                        shiftnum = int(line[j2][:line[j2].index('<')])
                    except ValueError:
                        break
                try:
                    period = int(line[j2 + 2][:line[j2 + 2].index('<')])
                except ValueError:
                    if line[j2 + 2][:line[j2 + 2].index('<')] == 'OT':
                        period = 4
                    else:
                        print('Error getting period in', line[j + 2])
                start = line[j2 + 4].split(' ')[0]
                end = line[j2 + 6].split(' ')[0]
                shift_data_startend[name].append([period, start, end])

        w = open(parsed_fname, 'w')
        w.write('TOIH {0:d} {1:d} {2:s}@{3:s}'.format(season, game, rname, hname))
        w.write('\nShift starts and ends')
        for p in player_order:
            w.write('\n{0:s}'.format(p))
            for i in range(len(shift_data_startend[p])):
                w.write('\n{0:d},{1:d},{2:s},{3:s}'.format(i + 1, shift_data_startend[p][i][0],
                                                           shift_data_startend[p][i][1],
                                                           shift_data_startend[p][i][2]))
        w.close()
    return hname, hdict


def parse_toiv(season, game, force_overwrite=False):
    """Checks if TOIV file needs parsing. If it does (or if force_overwrite=True), parses it."""

    fname = get_toiv_filename(season, game)
    parsed_fname = get_parsed_toiv_filename(season, game)
    rdict = {}
    rname = ''
    if force_overwrite or not os.path.isfile(parsed_fname):
        r = open(fname, 'r')
        data = r.read()
        r.close()

        data = data[data.index('img src') + 1:]
        rname = data[data.index('alt'):data.index('>')]
        rname = rname.split('"')[1]

        data = data[data.index('img src') + 1:]
        data = data[data.index('img src') + 1:]
        data = data[data.index('img src') + 1:]
        hname = data[data.index('alt'):data.index('>')]
        hname = hname.split('"')[1]

        data = data[data.index(rname) + 1:]
        try:
            data = data[data.index(rname) + 1:]
        except ValueError:
            pass

        data2 = data.split('playerHeading')

        shift_data_startend = {}
        player_order = []
        shift_data_matrix = [[] for i in range(3600)]

        for i in range(1, len(data2)):
            name = data2[i][data2[i].index('>') + 1:data2[i].index('<')]
            name_short = '#' + name[:name.index(',')]
            namei = name.index(' ')
            name = name[:namei] + ' ' + fixname(name[namei + 1:])
            rdict[name_short.upper()] = name[2:].strip()
            line = data2[i][data2[i].index('Start of Shift') + 1:]
            line = line[:line.index('Per')].split('>')
            shift_data_startend[name] = []
            player_order.append(name)
            for j in range(16, len(line), 14):
                j2 = j
                try:
                    shiftnum = int(line[j2][:line[j2].index('<')])
                except ValueError:
                    j2 = j + 1
                    try:
                        shiftnum = int(line[j2][:line[j2].index('<')])
                    except ValueError:
                        break
                try:
                    period = int(line[j2 + 2][:line[j2 + 2].index('<')])
                except ValueError:
                    if line[j2 + 2][:line[j2 + 2].index('<')] == 'OT':
                        period = 4
                    else:
                        print('Error getting period in', line[j2 + 2])
                start = line[j2 + 4].split(' ')[0]
                end = line[j2 + 6].split(' ')[0]
                shift_data_startend[name].append([period, start, end])

        w = open(parsed_fname, 'w')
        w.write('TOIB {0:d} {1:d} {2:s}@{3:s}'.format(season, game, rname, hname))
        w.write('\nShift starts and ends')
        for p in player_order:
            w.write('\n{0:s}'.format(p))
            for i in range(len(shift_data_startend[p])):
                w.write('\n{0:d},{1:d},{2:s},{3:s}'.format(i + 1, shift_data_startend[p][i][0],
                                                           shift_data_startend[p][i][1],
                                                           shift_data_startend[p][i][2]))
        w.close()
    return rname, rdict

def save_toimatrix(season, game, force_overwrite=False):
    """Uses parsed TOIH and TOIV to get matrix"""

    fname = get_parsed_toimatrix_filename(season, game)

    if force_overwrite or not os.path.isfile(fname):
        scoretimes = {0: '0-0'}
        home_positionmap = {'/a': 'F'}
        road_positionmap = {'/a': 'F'}
        prev_goal = False
        r = open(get_parsed_pbp_filename(season, game), 'r')
        for i in range(7):
            line = r.readline()
        while True:
            line = r.readline().split(',')
            if prev_goal:
                try:
                    scoretimes[convert_time(line[3])] = line[4]
                    prev_goal = False
                except ValueError:
                    print(str(line))
                    break
            if len(line) == 1:
                break
            if line[5] == 'GOAL':
                prev_goal = True

            players = line[12].split(';')
            if len(players) > 1:
                for p in players:
                    if p[1] == ' ':
                        pos = p[0]
                        name = p[2:]
                        if len(name) > 0:
                            if name[-1] == '\n':
                                name = name[:-1]
                            if name not in home_positionmap:
                                home_positionmap[name] = pos
                        else:
                            print(str(line))
            players = line[13].split(';')
            if len(players) > 1:
                for p in players:
                    pos = p[0]
                    name = p[2:]
                    if len(name) > 0:
                        if name[-1] == '\n':
                            name = name[:-1]
                        if name not in road_positionmap:
                            road_positionmap[name] = pos
                    else:
                        print(str(line))

        matrix = [[[], []] for i in range(3601)]

        for count, file in enumerate([get_parsed_toih_filename(season, game), get_parsed_toiv_filename(season, game)]):
            r = open(file, 'r')
            line = r.readline()
            line = r.readline()
            current_player = None
            while True:
                line = r.readline()[:-1]
                if ':' not in line:
                    current_player = line[2:].strip()
                    if current_player == '':
                        break
                else:
                    data = line.split(',')
                    per = int(data[1])
                    try:
                        start = convert_time(data[2], per)
                        end = convert_time(data[3], per) + 1
                        matrix += [[[], []] for i in range(max(end - len(matrix), 0))]
                        for i in range(start + 1, end):
                            matrix[i][count].append(current_player)
                    except ValueError:
                        print(str(line))

            r.close()

        w = open(get_parsed_toimatrix_filename(season, game), 'w')
        w.write('Time(s),Score,Strength,Home,Road')
        current_score = scoretimes[0]
        for i in range(1, len(matrix)):
            if i - 1 in scoretimes:
                current_score = scoretimes[i - 1]
            goalie1 = sum([1 if p in home_positionmap and home_positionmap[p] == 'G' else 0 for p in matrix[i][0]])
            goalie2 = sum([1 if p in road_positionmap and road_positionmap[p] == 'G' else 0 for p in matrix[i][1]])
            fixedstrength = ''
            if goalie1:
                fixedstrength += str(len(matrix[i][0]) - 1)
            else:
                fixedstrength += str(len(matrix[i][0]) - 1) + '+1'
            fixedstrength += 'v'
            if goalie2:
                fixedstrength += str(len(matrix[i][1]) - 1)
            else:
                fixedstrength += str(len(matrix[i][1]) - 1) + '+1'
            matrix[i][0] = ['{0:s} {1:s}'.format(home_positionmap[p], p) for p in matrix[i][0]]
            try:
                matrix[i][1] = ['{0:s} {1:s}'.format(road_positionmap[p], p) for p in matrix[i][1]]
            except KeyError as ke:
                if 'Scott Laughton' in str(ke):
                    road_positionmap['Scott Laughton'] = 'F'
                    matrix[i][1] = ['{0:s} {1:s}'.format(road_positionmap[p], p) for p in matrix[i][1]]

            w.write('\n{0:d},{1:s},{2:s},{3:s},{4:s}'.format(i, current_score, fixedstrength, ';'.join(matrix[i][0]),
                                                             ';'.join(matrix[i][1])))


def strip_out_html(lines):
    """Removes bold/italics etc and considers table, td, and tr

    <table> ... </table> constitutes a new table, <tr> ... </tr> a new row, and <td> ... </td> a new cell"""

    regex = re.compile('<')
    regex1 = re.compile('<tr')
    regex2 = re.compile('<td')
    regex3 = re.compile('<table')
    regex4 = re.compile('title="')

    startcells = [i.start() for i in regex2.finditer(lines)]
    startlines = [i.start() for i in regex1.finditer(lines)]
    starttables = [i.start() for i in regex3.finditer(lines)]
    starttitles = [i.start() for i in regex4.finditer(lines)]

    dct = {}

    for i in startcells:
        dct[i] = 'cell-s'
    for i in startlines:
        dct[i] = 'line-s'
    for i in starttables:
        dct[i] = 'table-s'
    for i in starttitles:
        dct[i] = 'title-s'
    indices = [i for i in dct.keys()]
    indices.sort()

    data = [[]]
    start = None
    end = None
    f_i = 0
    for i in range(len(indices) - 1):
        if dct[indices[i]] == 'table-s':
            data.append([])
        elif dct[indices[i]] == 'line-s':
            data[-1].append([])
        elif dct[indices[i]] == 'title-s':
            string = lines[indices[i] + 7:indices[i + 1]].strip()
            string = string[:string.index('"')]
            data[-1][-1].append(string)
        else:  # td
            string = lines[indices[i] + 3:indices[i + 1]].strip()
            string2 = ''
            while '>' in string:
                index = string.index('>')
                if '<' in string:
                    index2 = string.index('<')
                else:
                    index2 = len(string)
                string2 += string[index + 1: index2] + ' '
                string = string[index2 + 1:]

            string2 = string2.strip().replace('&nbsp;', ' ')
            string2 = string2.replace('\n;', '')
            if not string2 == '':
                data[-1][-1].append(string2.strip())

    return data

def get_teamlist(season):
    """Gets list of teams in a season"""
    exclude_teams = {'EAS', 'WES', 'ASB', 'ASR', 'BLU', 'RED', 'CEN', 'MET', 'PAC', 'ATL'}
    if season >= 2014:
        exclude_teams.add('PHX')
    else:
        exclude_teams.add('ARI')
    if season >= 2011:
        pass#exclude_teams.add('ATL')
    else:
        exclude_teams.add('WPG')
        exclude_teams.remove('ATL')
    return [team for team in TEAMS if team not in exclude_teams]


def write(season, force_overwrite=False):
    """Writes season data"""
    gamepages(season, force_overwrite)
    teampages(season, force_overwrite)


def fixname(name):
    """Fixes and reformats names"""
    name = name.strip()
    if ',' in name:
        name = name.split(',')
        name = name[1] + ' ' + name[0]
        name = name.strip()
    if len(name) > 0:
        if name[-1] == '\n':
            name = name[:-1]
        if name in NAMES:
            return NAMES[name]
        return formatname(name)
    else:
        print('problem with name:', name)
        return 'n/a'


def formatname(name):
    """Reformats names"""
    strings = name.strip().replace('  ', ' ').split(' ')
    for i in range(len(strings)):
        strings[i] = strings[i][0].upper() + strings[i][1:].lower()
    name = ' '.join(strings)
    if "O'" in name:
        i = name.index("O'")
        name = name[:i] + "O'" + name[i + 2].upper() + name[i + 3:]
    return name


def fix_penalty(penaltyname):
    """Fixes penalty name"""
    return PENALTIES[penaltyname]


def convert_time(time, period=0, countdown=False):
    """Converts time from seconds to min:sec in period, or vice versa. countdown=True-->start of period is 20:00
    countdown=true only works for regular season re: OT"""
    if not countdown:
        if isinstance(time, str):
            elap = int(time[:time.index(':')]) * 60 + int(time[time.index(':') + 1:])
            return 1200 * (period - 1) + elap
        else:
            min = time // 60
            time -= min * 60
            if time < 10:
                time = '0' + str(time)
            else:
                time = str(time)
            return '{0:d}:{1:s}'.format(min, time)
    else:
        if isinstance(time, str):
            elap = int(time[:time.index(':')]) * 60 + int(time[time.index(':') + 1:])
            if period == 4:
                return 1200 * (period - 1) + 300 - elap
            else:
                return 1200 * period - elap
        else:
            # TODO
            min = time // 60
            time -= min * 60
            if time < 10:
                time = '0' + str(time)
            else:
                time = str(time)
            return '{0:d}:{1:s}'.format(min, time)


def autoupdate(all_seasons=False, force_overwrite=False):
    """Updates current season data, automatically finding missing games"""
    if all_seasons:
        for season in range(2007, MAX_SEASON + 1):
            write(season, force_overwrite)
    else:
        write(MAX_SEASON, force_overwrite)


def get_season_gamelist(season):
    """Reads schedule page from NHL.com to get list of games this season"""
    gamelst = []
    for gametype in range(1, 4):  # 1 = preseason, 2 = reg season, 3 = playoffs
        urlstub = 'http://www2.nhl.com/ice/schedulebyseason.htm?season='
        url = urlstub + '{0:d}{1:d}&gameType={2:d}&team=&network=&venue='.format(season, season + 1, gametype)
        r = urllib.request.urlopen(url)
        data = r.read().decode().split('http://www.nhl.com/gamecenter/en/recap?id={0:d}'.format(season))
        # http://www.nhl.com/gamecenter/en/recap?id=2015020001
        r.close()
        for i in range(1, len(data)):
            gamelst.append(int(data[i][1:6]))
    return gamelst

def get_mascot_name(team):
    """Get team mascot name"""
    return MASCOT_NAMES[team.upper()]
