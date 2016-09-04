__author__ = 'muneebalam'

import GetPbP

SCORE_ADJUSTMENTS = {'micah': {-3: [0.841,1.234], -2: [0.869, 1.177], -1: [0.906, 1.115], 0: [0.973,1.029],
                                1: [1.038,0.965], 2:[1.098,0.918], 3: [1.158, 0.880]}, 'muneeb': {}}

RINK_BACKGROUND_FOLDER = GetPbP.get_additional_data_folder()

def get_teams(season):
    return GetPbP.get_teamlist(season)

def get_full_rink_filename(orientation='horizontal'):
    if orientation == 'horizontal':
        return '{0:s}horizontalrink.png'.format(RINK_BACKGROUND_FOLDER)
    else:
        return '{0:s}verticalrink.png'.format(RINK_BACKGROUND_FOLDER)

def get_bottom_rink_filename():
    return '{0:s}bottomrink.png'.format(RINK_BACKGROUND_FOLDER)

def get_left_rink_filename():
    return '{0:s}leftrink.png'.format(RINK_BACKGROUND_FOLDER)

def get_season_games(season, seg=['regular', 'playoff'], team1=None, team2=None):
    return GetPbP.get_season_saved_gamelist(season, seg, team1, team2)

def get_state(score1, score2):
    diff = score1 - score2
    if diff == 0:
        return 'tied'
    elif diff > 0:
        return 'lead{0:d}'.format(diff)
    else:
        return 'trail{0:d}'.format(abs(diff))


def read_muneeb_score_adjustments():
    """Reads my score adjustments for events into memory"""

    r = open(GetPbP.get_additional_data_folder() + 'event counts for weighting.csv')
    SCORE_ADJUSTMENTS['muneeb'] = {0: {}, 1: {}} #0 = home, 1 = road
    for line in r.read().strip().split('\n')[1:]:
        line2 = line.split(',')
        if line2[1] not in SCORE_ADJUSTMENTS['muneeb'][0]:
            SCORE_ADJUSTMENTS['muneeb'][0][line2[1]] = {}
            SCORE_ADJUSTMENTS['muneeb'][1][line2[1]] = {}
        SCORE_ADJUSTMENTS['muneeb'][0][line2[1]][int(line2[0])] = float(line2[-2])
        SCORE_ADJUSTMENTS['muneeb'][1][line2[1]][int(line2[0])] = float(line2[-1])
    r.close()


def score_adjust(info, perspective_team, method='Micah'):
    """Perspective team will be checked against acting team. Default method is @IneffectiveMath's for score-adj fenwick
    Can also adjust other event types with method='Muneeb'"""

    method = method.lower()

    score1, score2 = get_event_score(info)
    scorediff = score1 - score2
    if scorediff < -3:
        scorediff = -3
    elif scorediff > 3:
        scorediff = 3
    coefi = 0
    if info[0] == '@':
        coefi = 1
    if method == 'micah':
        if get_acting_team(info) == perspective_team:
            return SCORE_ADJUSTMENTS[method][scorediff][coefi]
        else:
            return SCORE_ADJUSTMENTS[method][-1 * scorediff][1 - coefi]
    elif method == 'muneeb':
        if method == 'muneeb' and len(SCORE_ADJUSTMENTS['muneeb']) == 0:
            read_muneeb_score_adjustments()
        if get_acting_team(info) == perspective_team:
            return SCORE_ADJUSTMENTS[method][coefi][get_event_type(info)][scorediff]
        else:
            return SCORE_ADJUSTMENTS[method][1 - coefi][get_event_type(info)][-1 * scorediff]


def check_type(info, allowedtypes):
    """Checks if event type is in allowedtypes"""
    if 'all' in allowedtypes:
        return True
    return (get_event_type(info) in allowedtypes)


def get_game(info):
    """Get game number of info"""
    return int(info[0])


def check_state(info, allowedstates):
    """Check if score state of info is in allowedstates"""
    state = get_state(*get_event_score(info))
    if 'all' in allowedstates or 'lead' in allowedstates and state[:-1] == 'lead' \
            or 'trail' in allowedstates and state[:-1] == 'trail' or state in allowedstates:
        return True
    return False


def check_zone(info, allowedzones):
    """Checks if zone of info is in allowedzones"""
    if 'all' in allowedzones:
        return True
    return get_event_zone(info) in allowedzones


def check_strength(info, allowedstrengths):
    """Checks if strength of info is in allowedstrengths"""
    if 'all' in allowedstrengths:
        return True
    return get_event_strength(info) in allowedstrengths


def get_event_num(info):
    if len(info[0]) == 5:
        print('Trying to get event number from team log')
        raise ValueError
    return int(info[0])


def get_event_period(info):
    """Gets event period"""
    if len(info[0]) == 5:
        return int(info[2])
    return int(info[1])


def get_event_strength(info):
    """Gets event strength"""
    if len(info[0]) == 5:
        if len(info) == 7:
            return info[4]
        return info[3]
    return info[2]


def get_event_time(info):
    """Gets event time (m:s)"""
    if len(info[0]) == 5:
        return info[4]
    return info[3]

def get_full_event_time(info):
    """Gets event time(seconds in the game)"""
    return convert_time(get_event_time(info), get_event_period(info))


def get_event_score(info):
    """Gets event score"""
    if len(info[0]) == 5:
        if len(info) == 7:
            return tuple([int(x) for x in info[3].split('-')])
        try:
            return tuple([int(x) for x in info[5].split('-')])
        except ValueError:
            return tuple([int(x) for x in info[2].split('-')])
    try:
        return tuple([int(x) for x in info[4].split('-')])
    except ValueError:
        return tuple([int(x) for x in info[1].split('-')])


def get_event_type(info):
    """Gets event type"""
    if len(info[0]) == 5:
        return info[6]
    return info[5]


def get_acting_team(info):
    """Gets acting team"""
    if len(info[0]) == 5:
        return info[7]
    return info[6]


def get_event_zone(info):
    """Gets event zone"""
    if len(info[0]) == 5:
        return info[8]
    return info[7]


def get_acting_player(info):
    """Gets acting player of info"""
    if len(info[0]) == 5:
        return info[9]
    return info[8]


def set_acting_player(info, p):
    """Changes acting player of info"""
    if len(info[0]) == 5:
        info[9] = p
    info[8] = p


def get_event_recipient(info):
    """Gets receiving player of info"""
    if len(info[0]) == 5:
        return info[10]
    return info[9]


def set_receiving_player(info, p):
    """Changes receiving player of info"""
    if len(info[0]) == 5:
        info[9] = p
    info[8] = p


def get_note(info):
    """Gets any notes in info"""
    if len(info[0]) == 5:
        return info[11]
    return info[10]


def get_assists(info):
    """Gets assisting players in info"""
    note = get_note(info)
    try:
        return [GetPbP.formatname(name) for name in note[note.index('Assist')+8:].strip().split(';')]
    except ValueError:
        return []
    except IndexError:
        return []

def set_assists(info, p1=None, p2=None):
    """Changes assisting players of info"""
    assists = get_assists(info)
    if len(assists) == 0:
        pass
    elif len(assists) == 1:
        if len(info[0]) == 5:
            info[11].replace(assists[0], p1)
        return info[10].replace(assists[0], p1)
    else:
        if len(info[0]) == 5:
            info[11].replace(assists[0], p1).replace(assists[1], p2)
        return info[10].replace(assists[0], p1).replace(assists[1], p2)


def get_shot_type(info):
    """Gets shot type in info"""
    stype = get_note(info).split(' ')[0]
    if stype not in {'Snap', 'Backhand', 'Slap', 'Wrist', 'Tip', 'Tip-In', 'Wrap', 'Deflected', 'Wrap-around'}:
        print(info)
    return stype


def get_penalty_type_length(info):
    """Gets penalty length of info"""
    line = get_note(info).split('(')
    try:
        return line[0].strip(), int(line[1][:2].strip())
    except ValueError:
        if line[0] in {'Fighting', 'Boarding', 'Spearing', 'Charging', 'Checking from behind'} or line[1] == 'maj)':
            return line[0], 5
        else:
            print('could not get penalty for', info)


def get_location(info, raw=False, return_none=True):
    """Gets event location"""
    if len(info[0]) == 5:
        line = info[12].split(';')
        x, y = line[0][1:], line[1][:-1]
        try:
            return int(x), int(y)
        except ValueError:
            if not return_none:
                raise ValueError
            else:
                return None, None
    line = info[11].split(';')
    x, y = line[0][1:], line[1][:-1]
    if raw:
        return x, y
    try:
        if get_event_period(info) % 2 == 0:
            return -1 * int(x), -1 * int(y) #so RHS locs = home, LHS locs = road
        else:
            return int(x), int(y)
    except ValueError:
        if not return_none:
            raise ValueError
        else:
            return None, None


def check_pos(posname, positions):
    """Checks if posname (e.g. F Alex Ovechkin) is in positions"""
    if 'all' in positions:
        return True
    if posname[0] in positions or posname[0] in ['L', 'R', 'C'] and 'F' in positions:
        return True
    return False


def get_home_players(info, pos=['F', 'D']):
    """Gets home players (or focus team players) of info"""
    if len(info[0]) == 5:
        if len(info) == 7:
            return [x[2:][:-1] if x[-1] == '\n' else x[2:] for x in info[5].split(';') if check_pos(x, pos)]
        try:
            return [x[2:][:-1] if x[-1] == '\n' else x[2:] for x in info[13].split(';') if check_pos(x, pos)]
        except IndexError:
            return [x[2:][:-1] if x[-1] == '\n' else x[2:] for x in info[4].split(';') if check_pos(x, pos)]
    try:
        return [x[2:][:-1] if x[-1] == '\n' else x[2:] for x in info[12].split(';') if check_pos(x, pos)]
    except IndexError:
        return [x[2:][:-1] if x[-1] == '\n' else x[2:] for x in info[3].split(';') if check_pos(x, pos)]


def get_road_players(info, pos=['F', 'D']):
    """Gets road players (or not-focus team players) of info"""
    if len(info[0]) == 5:
        if len(info) == 7:
            return [x[2:][:-1] if x[-1] == '\n' else x[2:] for x in info[6].split(';') if check_pos(x, pos)]
        try:
            return [x[2:][:-1] if x[-1] == '\n' else x[2:] for x in info[14].split(';') if check_pos(x, pos)]
        except IndexError:
            return [x[2:][:-1] if x[-1] == '\n' else x[2:] for x in info[5].split(';') if check_pos(x, pos)]
    try:
        return [x[2:][:-1] if x[-1] == '\n' else x[2:] for x in info[13].split(';') if check_pos(x, pos)]
    except IndexError:
        return [x[2:][:-1] if x[-1] == '\n' else x[2:] for x in info[4].split(';') if check_pos(x, pos)]


def read_game_corsi(season, game, states=['all'], strengths=['5v5']):
    """Reads corsi from this game"""
    return read_game_pbp(season, game, types=['GOAL', 'SHOT', 'MISS', 'BLOCK'], states=states, strengths=strengths)


def read_game_pbp(season, game, types=['all'], strengths=['5v5'], states=['all'], zones=['all']):
    """Returns events which satisfy given criteria"""
    try:
        r = open(GetPbP.get_parsed_pbp_filename(season, game), 'r')
    except FileNotFoundError:
        print('No PBP for {0:d} {1:d}'.format(season, game))
        return
    for i in range(7):
        line = r.readline()
    while True:
        line = r.readline().split(',')
        if len(line) == 1:
            break
        if check_type(line, types) and check_strength(line, strengths) and check_state(line, states) and \
                check_zone(line, zones):
            yield line
    r.close()

def read_game_toi(season, game, strengths=['5v5'], states=['all']):
    """Returns seconds which satisfy given criteria"""

    r = open(GetPbP.get_parsed_toimatrix_filename(season, game))
    r.readline()
    while True:
        line = r.readline().split(',')
        if len(line) == 1:
            break
        if check_state(line, states) and check_strength(line, strengths):
            yield line
    r.close()


def read_team_corsi(team, season, states=['all']):
    """Reads corsi from this team and season"""
    return read_team_pbp(team, season, types=['GOAL', 'SHOT', 'MISS', 'BLOCK'], states=states)


def all_players_on(info, plist):
    """Checks if all players in plist are on ice for this event"""
    ps = get_home_players(info) + get_road_players(info)
    if not isinstance(plist, list):
        plist = [plist]
    for p in plist:
        if p not in ps:
            return False
    return True

def all_players_off(info, plist):
    """Checks if all players in plist are off ice for this event"""
    ps = set(get_home_players(info) + get_road_players(info))
    if not isinstance(plist, list):
        plist = [plist]
    for p in plist:
        if p in ps:
            return False
    return True


def read_team_pbp(team, season, types=['all'], strengths=['5v5'], states=['all'], players_on=None, zones=['all'],
                  players_off=None):
    """Returns events which satisfy given criteria"""

    try:
        r = open(GetPbP.get_team_pbplog_filename(season, team), 'r')
    except FileNotFoundError:
        print('No PBP for {0:d} {1:d}'.format(season, team))
        return
    for i in range(1):
        line = r.readline()
    while True:
        line = r.readline().rstrip().split(',')
        if len(line) == 1:
            break
        if check_type(line, types) and check_strength(line, strengths) and check_state(line, states) and \
                check_zone(line, zones) and (players_on is None or all_players_on(line, players_on)) and \
                (players_off is None or all_players_off(line, players_off)):
            yield line
    r.close()

def read_team_toi(team, season, strengths=['5v5'], states=['all']):
    """Returns seconds which satisfy given criteria"""

    r = open(GetPbP.get_team_toilog_filename(season, team))
    r.readline()
    while True:
        line = r.readline().split(',')
        if len(line) == 1:
            break
        if check_state(line, states) and check_strength(line, strengths):
            yield line
    r.close()


def get_home_player_numbers(season, games, switch=None):
    """Get home player numbers from this game using TOI log"""
    dct = {}
    for game in games:
        if switch is None or not switch[game]:
            for p, num in get_player_numbers(GetPbP.get_parsed_toih_filename(season, game)).items():
                dct[p] = num
        else:
            for p, num in get_player_numbers(GetPbP.get_parsed_toiv_filename(season, game)).items():
                dct[p] = num
    return dct


def get_road_player_numbers(season, games, switch=None):
    """Get road playernumbers from this game using TOI log"""
    dct = {}
    for game in games:
        if switch is None or not switch[game]:
            for p, num in get_player_numbers(GetPbP.get_parsed_toiv_filename(season, game)).items():
                dct[p] = num
        else:
            for p, num in get_player_numbers(GetPbP.get_parsed_toih_filename(season, game)).items():
                dct[p] = num
    return dct


def get_player_numbers(toifilename):
    """Get player numbers from TOI file"""
    nums = {}
    r = open(toifilename, 'r')
    data = r.read().split('\n')[2:]
    r.close()
    for line in data:
        if ':' not in line:
            nums[line[2:].strip()] = int(line[:2].strip())
    return nums


def h2h_chart_data(season, games, strengths=['5v5']):
    """Get H2H chart data from this game"""
    rnames = []
    hnames = []
    switch = {}
    if not isinstance(games, list):
        games = [games]
    for game in games:
        try:
            r = open(GetPbP.get_parsed_pbp_filename(season, game))
        except FileNotFoundError:
            print('No PBP for {0:d} {1:d}'.format(season, game))
            return
        line = r.readline()
        rname, hname = line[line.index(':') + 1:].strip().split('@')
        rnames.append(rname)
        hnames.append(hname)
        if len(rnames) == 1:
            switch[game] = False
        else:
            if rname == rnames[0]:
                switch[game] = False
            else:
                switch[game] = True
        r.close()

    h2htoi = {}
    hwhtoi_h = {}
    hwhtoi_r = {}
    htotalstoi = {}
    rtotalstoi = {}
    home_line_toi = {}
    road_line_toi = {}

    horder = []
    horderset = set({})
    rorder = []
    rorderset = set({})

    hnumbers = get_home_player_numbers(season, games, switch)
    rnumbers = get_road_player_numbers(season, games, switch)

    for position in ['F', 'D']:
        for game in games:
            for line in read_game_toi(season, game, strengths):
                if not switch[game]:
                    rp = get_road_players(line, [position])
                    hp = get_home_players(line, [position])
                else:
                    hp = get_road_players(line, [position])
                    rp = get_home_players(line, [position])
                rp.sort()
                hp.sort()
                hline = ';'.join(hp)
                rline = ';'.join(rp)

                for r in rp:
                    if r not in rtotalstoi:
                        rtotalstoi[r] = 0
                        road_line_toi[r] = {}
                    rtotalstoi[r] += 1
                    if rline not in road_line_toi[r]:
                        road_line_toi[r][rline] = 0
                    road_line_toi[r][rline] += 1

                for h in hp:
                    if h not in htotalstoi:
                        htotalstoi[h] = 0
                        home_line_toi[h] = {}
                    htotalstoi[h] += 1
                    if hline not in home_line_toi[h]:
                        home_line_toi[h][hline] = 0
                    home_line_toi[h][hline] += 1

        for i in range(len(htotalstoi)):
            max_val = None
            for p in htotalstoi:
                if p not in horderset:
                    if max_val is None or htotalstoi[p] > htotalstoi[max_val]:
                        max_val = p
            if max_val is None:
                break
            horder.append(max_val)
            horderset.add(max_val)

            max_line = None
            for line in home_line_toi[max_val]:
                if max_line is None or home_line_toi[max_val][line] > home_line_toi[max_val][max_line]:
                    max_line = line
            line2 = max_line.split(';')
            line2.remove(max_val)
            if len(line2) > 0:
                if line2[0] not in horderset:
                    horder.append(line2[0])
                    horderset.add(line2[0])
                if position == 'F' and len(line2) > 1:
                    if line2[1] not in horderset:
                        horder.append(line2[1])
                        horderset.add(line2[1])

        for i in range(len(rtotalstoi)):
            max_val = None
            for p in rtotalstoi:
                if p not in rorderset:
                    if max_val is None or rtotalstoi[p] > rtotalstoi[max_val]:
                        max_val = p
            if max_val is None:
                break
            rorder.append(max_val)
            rorderset.add(max_val)

            max_line = None
            for line in road_line_toi[max_val]:
                if max_line is None or road_line_toi[max_val][line] > road_line_toi[max_val][max_line]:
                    max_line = line
            line2 = max_line.split(';')
            line2.remove(max_val)
            if len(line2) > 0:
                if line2[0] not in rorderset:
                    rorder.append(line2[0])
                    rorderset.add(line2[0])
                if position == 'F' and len(line2) > 1:
                    if line2[1] not in rorderset:
                        rorder.append(line2[1])
                        rorderset.add(line2[1])
        if position == 'F':
            num_fs = (len(horder), len(rorder))
    horder.reverse()
    h2hcf = {}
    homecf = 0
    roadcf = 0
    rcorsi = {p: 0 for p in rorder}
    hcorsi = {p: 0 for p in horder}
    hwhcf_h = {}
    hwhcf_r = {}
    for gamecount, game in enumerate(games):
        for line in read_game_corsi(season, game, strengths=strengths):
            if not switch[game]:
                rp = get_road_players(line)
                hp = get_home_players(line)
                if get_acting_team(line) == GetPbP.TEAM_MAP[hnames[gamecount]]:
                    ev_for = 1
                    homecf += 1
                else:
                    ev_for = -1
                    roadcf += 1
            else:
                hp = get_road_players(line)
                rp = get_home_players(line)

                if get_acting_team(line) == GetPbP.TEAM_MAP[hnames[gamecount]]:
                    ev_for = -1
                    roadcf += 1
                else:
                    ev_for = 1
                    homecf += 1

            for h in hp:
                if h not in h2hcf:
                    h2hcf[h] = {}
                    hwhcf_h[h] = {}
                for r in rp:
                    if r not in h2hcf[h]:
                        h2hcf[h][r] = 0
                    h2hcf[h][r] += ev_for
                for h2 in hp:
                    if h2 not in hwhcf_h[h]:
                        hwhcf_h[h][h2] = 0
                    hwhcf_h[h][h2] += ev_for
            for h in hp:
                hcorsi[h] += ev_for
            for r in rp:
                rcorsi[r] -= ev_for
                if r not in hwhcf_r:
                    hwhcf_r[r] = {}
                for r2 in rp:
                    if r2 not in hwhcf_r[r]:
                        hwhcf_r[r][r2] = 0
                    hwhcf_r[r][r2] -= ev_for
    for gamecount, game in enumerate(games):
        for line in read_game_toi(season, game, strengths):
            if not switch[game]:
                rp = get_road_players(line)
                hp = get_home_players(line)
            else:
                hp = get_road_players(line)
                rp = get_home_players(line)
            for h in hp:
                if h not in h2htoi:
                    h2htoi[h] = {}
                    hwhtoi_h[h] = {}
                for r in rp:
                    if r not in h2htoi[h]:
                        h2htoi[h][r] = 0
                    h2htoi[h][r] += 1
                for h2 in hp:
                    if h2 not in hwhtoi_h[h]:
                        hwhtoi_h[h][h2] = 0
                    hwhtoi_h[h][h2] += 1
            for r in rp:
                if r not in hwhtoi_r:
                    hwhtoi_r[r] = {}
                for r2 in rp:
                    if r2 not in hwhtoi_r[r]:
                        hwhtoi_r[r][r2] = 0
                    hwhtoi_r[r][r2] += 1

    return ((hnames[0], rnames[0]), (horder, rorder), (hnumbers, rnumbers), (homecf, roadcf), (hcorsi, rcorsi), h2hcf,
            (hwhcf_h, hwhcf_r), (htotalstoi, rtotalstoi), h2htoi, (hwhtoi_h, hwhtoi_r), num_fs)


def toi_over_games(num_games, strengths, force_overwrite=False):
    """Sum over TOI from given games at given strengths"""
    import os
    import os.path
    filename = '/Users/muneebalam/Desktop/toi by game {0:s}.csv'.format(str(strengths))
    filename2 = '/Users/muneebalam/Desktop/toi query output.csv'
    gameset = set()
    toi_by_game = {}
    gamelist = []
    if not isinstance(strengths, list):
        strengths = [strengths]
    if not force_overwrite and os.path.isfile(filename):
        r = open(filename, 'r')
        data = r.read().split('\n')
        r.close()
        try:
            gamelist = [int(x) for x in data[0][6:].split(' ')]
            gameset = set(gamelist)
            for x in range(2, len(data)):
                line = data[x].split(',')
                toi_by_game[line[0]] = [int(line[x]) for x in range(1, len(line))]
        except ValueError as ve:
            print(ve)
    season_games = os.listdir(GetPbP.get_parsed_gamesheet_folder(2015))
    games_added = []
    for file in season_games:
        if file[-8:] == 'TOIM.csv':
            game = int(file[:5])
            if game not in gameset and game >= 20001:
                gameset.add(game)
                games_added.append(game)
                gamelist.append(game)
                this_game_players_seen = set()
                for sec in read_game_toi(2015, game, strengths):
                    players_on = get_home_players(sec) + get_road_players(sec)
                    for p in players_on:
                        if p not in this_game_players_seen:
                            this_game_players_seen.add(p)
                            if p not in toi_by_game:
                                toi_by_game[p] = []
                            toi_by_game[p].append(0)
                        toi_by_game[p][-1] += 1
    print('Finished reading {0:d} new game(s)'.format(len(games_added)))
    if len(games_added) > 0:
        writer = open(filename, 'w')
        writer.write('Games,{0:s}'.format(' '.join([str(x) for x in gamelist])))
        writer.write('\nName,{0:s}'.format(','.join([str(x) for x in range(1,
                                                                max([len(gmtoi) for gmtoi in toi_by_game.values()]) + 1)])))
        for p in toi_by_game:
            writer.write('\n{0:s},{1:s}'.format(p, ','.join([str(toi_by_game[p][x])
                                                             for x in range(len(toi_by_game[p]))])))
        writer.close()

    w = open(filename2, 'w')
    w.write('# Games: {0:d}'.format(num_games))
    w.write('\nStrengths: {0:s}'.format(' '.join(strengths)))
    w.write('\nName,GP,TOI (min)')
    for p in toi_by_game:
        toi = sum(toi_by_game[p][max(0, len(toi_by_game[p]) - num_games):])
        w.write('\n{0:s},{1:d},{2:.2f}'.format(p, min(len(toi_by_game[p]), num_games), toi/60))
    w.close()

def get_game_shot_locations(season, game, types=['GOAL', 'SHOT'], strengths=['5v5'], states=['all']):
    """Returns x, y tuples for shot locations for given game. Home team on right, road on left"""

    locs = {}
    for line in read_game_pbp(season, game, types, strengths, states):
        t = get_acting_team(line)
        if t not in locs:
            locs[t] = []
        locs[t].append(get_location(line))
    return locs


def get_game_summary_filename(season, game):
    """Returns the *full* filename for game summary for the given game from given season.

    season: e.g. 2013 for 2013-14
    game: five-digit number format (from 20001 to 21230 for regular season)"""

    return '{0:s}{1:d} H2HSUM.csv'.format(GetPbP.get_parsed_gamesheet_folder(season), game)

def create_game_h2h_summary(season, game, force_overwrite=False):
    """Summarizes 5v5 h2h player stats for this game: TOI, CF, CA"""
    import os
    fname = get_game_summary_filename(season, game)
    w = None
    if force_overwrite or not os.path.isfile(fname):
        try:
            r = open(GetPbP.get_parsed_pbp_filename(season, game), 'r')
            data = r.read().split('\n')
            r.close()

            w = open(fname, 'w')

            rname, hname = data[0][data[0].index(':') + 1:].strip().split('@')
            rshort = GetPbP.TEAM_MAP[rname]
            hshort = GetPbP.TEAM_MAP[hname]
            w.write('{0:d} {1:d}:{2:s}@{3:s}\n5v5 game summary'.format(season, game, rname, hname))
            data = [line.split(',') for line in data]

            h2htoi = {}
            line_toi = {}
            home_players = []
            road_players = []
            for line in read_game_toi(season, game):
                rp = get_road_players(line)
                hp = get_home_players(line)
                for p in rp:
                    if p not in h2htoi:
                        road_players.append(p)
                for p in hp:
                    if p not in h2htoi:
                        home_players.append(p)
                for p in rp + hp:
                    if p not in h2htoi:
                        h2htoi[p] = {}
                    for p2 in rp + hp:
                        if p2 not in h2htoi[p]:
                            h2htoi[p][p2] = 0
                        h2htoi[p][p2] += 1
                rline = tuple(sorted(get_road_players(line, ['F'])))
                if rline not in line_toi:
                    line_toi[rline] = 0
                line_toi[rline] += 1
                hline = tuple(sorted(get_home_players(line, ['F'])))
                if hline not in line_toi:
                    line_toi[hline] = 0
                line_toi[hline] += 1
            if len(h2htoi) == 0:
                w.write('\nIncomplete data')
                w.close()
                return
            h2htoi = {p: {p2: h2htoi[p][p2] if p2 in h2htoi[p] else 0 for p2 in h2htoi} for p in h2htoi}
            h2h = {p: {p2: [0, 0] for p2 in h2htoi} for p in h2htoi} #[cf, ca]
            line_cf = {line: [0, 0] for line in line_toi}
            cev_lst = []
            corsi_events = {'GOAL', 'SHOT', 'MISS', 'BLOCK'}
            for line in data[6:]:
                if check_strength(line, ['5v5']) and get_event_type(line) in corsi_events:
                    rp = get_road_players(line)
                    rline = tuple(sorted(get_road_players(line, ['F'])))
                    hp = get_home_players(line)
                    hline = tuple(sorted(get_home_players(line, ['F'])))
                    if rline not in line_cf:
                        line_cf[rline] = [0, 0]
                        line_toi[rline] = 0
                    if hline not in line_cf:
                        line_cf[hline] = [0, 0]
                        line_toi[hline] = 0
                    for p in rp + hp:
                        if p not in h2h:
                            h2h[p] = {p: 0}
                    if get_acting_team(line) == hshort:
                        line_cf[hline][0] += 1
                        line_cf[rline][1] += 1
                        cev_lst.append((hp, rp))
                    else:
                        line_cf[hline][1] += 1
                        line_cf[rline][0] += 1
                        cev_lst.append((rp, hp))
            h2htoi = {p: {p2: h2htoi[p][p2] if p2 in h2htoi[p] else 0 for p2 in h2htoi} for p in h2htoi}
            h2h = {p: {p2: h2h[p][p2] if p2 in h2h[p] else [0, 0] for p2 in h2htoi} for p in h2htoi}
            for i in range(len(cev_lst)):
                for p1 in cev_lst[i][0]:
                    if p1 not in h2h:
                        h2h[p1] = {}
                        h2htoi[p1] = {}
                    for p2 in cev_lst[i][0] + cev_lst[i][1]:
                        if p2 not in h2h[p1]:
                            h2h[p1][p2] = [0, 0]
                            h2htoi[p1][p2] = 0
                        h2h[p1][p2][0] += 1
                for p1 in cev_lst[i][1]:
                    if p1 not in h2h:
                        h2h[p1] = {}
                        h2htoi[p1] = {}
                    for p2 in cev_lst[i][0] + cev_lst[i][1]:
                        if p2 not in h2h[p1]:
                            h2h[p1][p2] = [0, 0]
                            h2htoi[p1][p2] = 0
                        h2h[p1][p2][1] += 1
            w.write('\nH2H data: [TOI CF CA]')
            w.write('\nHome player order,{0:s}'.format(','.join(home_players)))
            w.write('\nRoad player order,{0:s}'.format(','.join(road_players)))
            w.write('\nHome-Home')
            for p in home_players:
                w.write('\n{0:s}'.format(p))
                for p2 in home_players:
                    w.write(',{0:d} {1:d} {2:d}'.format(h2htoi[p][p2], h2h[p][p2][0], h2h[p][p2][1]))
            w.write('\nHome-Road')
            for p in home_players:
                w.write('\n{0:s}'.format(p))
                for p2 in road_players:
                    w.write(',{0:d} {1:d} {2:d}'.format(h2htoi[p][p2], h2h[p][p2][0], h2h[p][p2][1]))
            w.write('\nRoad-Road')
            for p in road_players:
                w.write('\n{0:s}'.format(p))
                for p2 in road_players:
                    w.write(',{0:d} {1:d} {2:d}'.format(h2htoi[p][p2], h2h[p][p2][0], h2h[p][p2][1]))
            home_players = set(home_players)
            w.write('\nHome lines\nPlayers,TOI,CF,CA')
            for line in line_toi:
                if len(line) > 0 and line[0] in home_players:
                    w.write('\n{0:s},{1:d},{2:d},{3:d}'.format(';'.join(line), line_toi[line], line_cf[line][0],
                                                           line_cf[line][1]))
            w.write('\nRoad lines\nPlayers,TOI,CF,CA')
            for line in line_toi:
                if len(line) > 0 and line[0] not in home_players:
                    w.write('\n{0:s},{1:d},{2:d},{3:d}'.format(';'.join(line), line_toi[line], line_cf[line][0],
                                                           line_cf[line][1]))
            w.close()
        except FileNotFoundError:
            if game <= 21230:
                print('Could not make summary for', season, game)
            if w is not None:
                w.close()
        except ValueError as ve:
            if season == 2011 and game == 20259:
                pass
            else:
                print('Value error in', season, game, ve)
            if w is not None:
                w.close()

def pp_formation(team, seasons, strength=['5v4']):
    """Estimates PP formation and plays based on shot locations, goal locations, and assist numbers"""

    #new approach--look at shots to get five centers. Look at where goals came from and which center is closest;
    #look at who got assist, where they usually shoot from, categorize them under that center

    import ChartMethods

    if not isinstance(seasons, list):
        seasons = [seasons]
    if not isinstance(strength, list):
        strength = [strength]
    sf = []
    for season in seasons:
        for line in read_team_pbp(team, season, types=['GOAL', 'SHOT', 'MISS'], strengths=strength):
            if get_acting_team(line) == team:
                if get_location(line)[0] is not None:
                    sf.append(line)
    top_shooters = {}
    for shot in sf:
        shooter = get_acting_player(shot)
        if shooter not in top_shooters:
            top_shooters[shooter] = 0
        top_shooters[shooter] += 1
    tops = set()
    for i in range(5):
        max_val = None
        for shooter in top_shooters:
            if shooter not in tops and (max_val is None or top_shooters[shooter] > top_shooters[max_val]):
                max_val = shooter
        tops.add(max_val)
    import matplotlib.pyplot as plt
    ChartMethods.rink_background('hfull')
    topshotlst = {shooter: [] for shooter in tops}
    for shot in sf:
        shooter = get_acting_player(shot)
        if shooter in tops:
            topshotlst[shooter].append(get_location(shot))
    colors = {0: 'c', 1: 'r', 2: 'g', 3: 'b', 4: 'k'}
    for i, shooter in enumerate(topshotlst.keys()):
        colors[shooter] = colors[i]
    for shooter, shots in topshotlst.items():
        plt.scatter([-1 * shot[0] for shot in shots], [-1 * shot[1] for shot in shots], c=colors[shooter],
                    s=100, label=shooter)
    plt.legend(loc='center', scatterpoints=1, prop={'size':8})
    plt.axis('off')
    plt.tight_layout()

    from sklearn.cluster import KMeans
    shotlocs = [get_location(shot) for shot in sf]

    plt.show()


def convert_time(time, period=0, countdown=False):
    """Convert m:s time in given period to seconds elapsed in game"""
    return GetPbP.convert_time(time, period, countdown)

def get_gamebygame_data_filename(season):
    """Helper method for Tableau charts"""
    return '{0:s}{1:d} gamebygame.csv'.format(GetPbP.get_parsed_gamesheet_folder(season), season)

def gen_gamebygame(season):
    """Helper method for Tableau charts"""
    w = open(get_gamebygame_data_filename(season), 'w')
    w.write('Player,Team,Pos,Game,Season,Date,TOION(60s),CFON,CAON,TOIOFF(60s),CFOFF,CAOFF,GFON,GAON,GFOFF,GAOFF,')
    w.write('FComp,DComp,FTeam,DTeam,F Faced,D Faced,F With,D With,DZS,NZS,OZS,iG,iCF')
    fqoc = {}
    dqoc = {}
    fqot = {}
    dqot = {}
    posmap = {}
    playerids = {}
    playerids[season] = {}
    fqoc[season] = {}
    dqoc[season] = {}
    fqot[season] = {}
    dqot[season] = {}
    for game in get_season_games(season):
        fqoc[season][game] = {}
        fqot[season][game] = {}
        dqoc[season][game] = {}
        dqot[season][game] = {}
        try:
            homecf = 0
            homeca = 0
            homegf = 0
            homega = 0
            hometoi = 0
            gamedata = {'Home': {}, 'Road': {}}
            r = open(GetPbP.get_parsed_pbp_filename(season, game), 'r')
            headers = r.readline()
            rname = GetPbP.TEAM_MAP[headers[headers.index(':') + 2:headers.index('@')]]
            hname = GetPbP.TEAM_MAP[headers[headers.index('@') + 1:].rstrip()]
            date = r.readline().rstrip()
            date = date[date.index(',') + 2:]
            month = date[:3]
            day = int(date[date.index(' ') + 1:date.index(',')])
            if day < 10:
                day = '0' + str(day)
            else:
                day = str(day)
            yr = date[-2:]
            date = '{0:s}-{1:s}-{2:s}'.format(day, month, yr)  # DD-Mmm-YY
            r.close()

            for line in read_game_toi(season, game):
                hf = get_home_players(line, ['F'])
                for p in hf:
                    posmap[hname + p] = 'F'
                hd = get_home_players(line, ['D'])
                for p in hd:
                    posmap[hname + p] = 'D'
                rf = get_road_players(line, ['F'])
                for p in rf:
                    posmap[rname + p] = 'F'
                rd = get_road_players(line, ['D'])
                for p in rd:
                    posmap[rname + p] = 'D'
                for p in hf + hd:
                    name = hname + p
                    if name not in playerids[season]:
                        playerids[season][name] = len(playerids[season])
                for p in rf + rd:
                    name = rname + p
                    if name not in playerids[season]:
                        playerids[season][name] = len(playerids[season])
                for p in hf + hd:
                    p2 = hname + p
                    if playerids[season][p2] not in fqoc[season][game]:
                        fqoc[season][game][playerids[season][p2]] = []
                        fqot[season][game][playerids[season][p2]] = []
                        dqoc[season][game][playerids[season][p2]] = []
                        dqot[season][game][playerids[season][p2]] = []

                for p in rf + rd:
                    p2 = rname + p
                    if playerids[season][p2] not in fqoc[season][game]:
                        fqoc[season][game][playerids[season][p2]] = []
                        fqot[season][game][playerids[season][p2]] = []
                        dqoc[season][game][playerids[season][p2]] = []
                        dqot[season][game][playerids[season][p2]] = []

                #qoc
                for hp in hf:
                    p = hname + hp
                    for rp in rf:
                        p2 = rname + rp
                        fqoc[season][game][playerids[season][p]].append(playerids[season][p2])
                        fqoc[season][game][playerids[season][p2]].append(playerids[season][p])
                    for rp in rd:
                        p2 = rname + rp
                        dqoc[season][game][playerids[season][p]].append(playerids[season][p2])
                        fqoc[season][game][playerids[season][p2]].append(playerids[season][p])
                for hp in hd:
                    p = hname + hp
                    for rp in rf:
                        p2 = rname + rp
                        fqoc[season][game][playerids[season][p]].append(playerids[season][p2])
                        dqoc[season][game][playerids[season][p2]].append(playerids[season][p])
                    for rp in rd:
                        p2 = rname + rp
                        dqoc[season][game][playerids[season][p]].append(playerids[season][p2])
                        dqoc[season][game][playerids[season][p2]].append(playerids[season][p])

                #qot
                for hp in hf + hd:
                    p = hname + hp
                    for hp2 in hf:
                        p2 = hname + hp2
                        if not p == p2:
                            fqot[season][game][playerids[season][p]].append(playerids[season][p2])
                    for hp2 in hd:
                        p2 = hname + hp2
                        if not p == p2:
                            dqot[season][game][playerids[season][p]].append(playerids[season][p2])
                for rp in rf + rd:
                    p = rname + rp
                    for rp2 in rf:
                        p2 = rname + rp2
                        if not p == p2:
                            fqot[season][game][playerids[season][p]].append(playerids[season][p2])
                    for rp2 in rd:
                        p2 = rname + rp2
                        if not p == p2:
                            dqot[season][game][playerids[season][p]].append(playerids[season][p2])

                hps = hf + hd
                rps = rf + rd
                hometoi += 1
                for p in hps:
                    if p not in gamedata['Home']:
                        gamedata['Home'][p] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    gamedata['Home'][p][2] += 1
                for p in rps:
                    if p not in gamedata['Road']:
                        gamedata['Road'][p] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    gamedata['Road'][p][2] += 1

            for line in read_game_corsi(season, game):
                hps = get_home_players(line, ['F', 'D'])
                rps = get_road_players(line, ['F', 'D'])
                goal = get_event_type(line) == 'GOAL'
                shooter = get_acting_player(line)

                if get_acting_team(line) == hname:
                    homecf += 1
                    if goal:
                        homegf += 1
                    for p in hps:
                        if p not in gamedata['Home']:
                            gamedata['Home'][p] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                            #[cf, ca, toi, gf, ga, dz, nz, oz, ig, icf]
                        gamedata['Home'][p][0] += 1
                        if goal:
                            gamedata['Home'][p][3] += 1
                    for p in rps:
                        if p not in gamedata['Road']:
                            gamedata['Road'][p] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        gamedata['Road'][p][1] += 1
                        if goal:
                            gamedata['Road'][p][4] += 1
                    if shooter not in gamedata['Home']:
                        gamedata['Home'][shooter] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    gamedata['Home'][shooter][6] += 1
                    if goal:
                        gamedata['Home'][shooter][5] += 1
                else:
                    homeca += 1
                    if goal:
                        homega += 1
                    for p in hps:
                        if p not in gamedata['Home']:
                            gamedata['Home'][p] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        gamedata['Home'][p][1] += 1
                        if goal:
                            gamedata['Home'][p][4] += 1
                    for p in rps:
                        if p not in gamedata['Road']:
                            gamedata['Road'][p] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        gamedata['Road'][p][0] += 1
                        if goal:
                            gamedata['Road'][p][3] += 1
                    if shooter not in gamedata['Road']:
                        gamedata['Road'][shooter] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    gamedata['Road'][shooter][6] += 1
                    if goal:
                        gamedata['Road'][shooter][5] += 1
            for line in read_game_pbp(season, game, ['FAC']):
                hps = get_home_players(line, ['F', 'D'])
                rps = get_road_players(line, ['F', 'D'])
                for p in hps:
                    if p not in gamedata['Home']:
                        gamedata['Home'][p] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                for p in rps:
                    if p not in gamedata['Road']:
                        gamedata['Road'][p] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                ez = get_event_zone(line)
                act = get_acting_team(line)
                if ez == 'Def':
                    if act == hname:
                        for p in hps:
                            gamedata['Home'][p][5] += 1
                        for p in rps:
                            gamedata['Road'][p][7] += 1
                    else:
                        for p in hps:
                            gamedata['Home'][p][7] += 1
                        for p in rps:
                            gamedata['Road'][p][5] += 1
                elif ez == 'Off':
                    if act == hname:
                        for p in hps:
                            gamedata['Home'][p][7] += 1
                        for p in rps:
                            gamedata['Road'][p][5] += 1
                    else:
                        for p in hps:
                            gamedata['Home'][p][5] += 1
                        for p in rps:
                            gamedata['Road'][p][7] += 1
                else:
                    for p in hps:
                        gamedata['Home'][p][6] += 1
                    for p in rps:
                        gamedata['Road'][p][6] += 1

            for p in gamedata['Home']:
                try:
                    pos = posmap[hname+p]
                    lst = [p, hname, pos, str(game), str(season), date, str(gamedata['Home'][p][2] / 3600),
                           str(gamedata['Home'][p][0]), str(gamedata['Home'][p][1]),
                           str((hometoi - gamedata['Home'][p][2]) / 3600), str(homecf - gamedata['Home'][p][0]),
                           str(homeca - gamedata['Home'][p][1]),
                           str(gamedata['Home'][p][3]), str(gamedata['Home'][p][4]),
                           str(homegf - gamedata['Home'][p][3]),
                           str(homega - gamedata['Home'][p][4]),
                           str(gamedata['Home'][p][5]), str(gamedata['Home'][p][6]), str(gamedata['Home'][p][7]),
                           str(gamedata['Home'][p][8]), str(gamedata['Home'][p][9])]
                    w.write('\n{0:s}'.format(','.join(lst)))
                except KeyError:
                    if not p[0] == '#':
                        print(season, game, hname, rname, hname+p)
                    #print([key for key in posmap.keys() if key[:3] == hname])
                    #print([key for key in posmap.keys() if key[:3] == rname])
                    #raise KeyError
            for p in gamedata['Road']:
                try:
                    pos = posmap[rname+p]
                    lst = [p, rname, pos, str(game), str(season), date, str(gamedata['Road'][p][2] / 3600),
                           str(gamedata['Road'][p][0]), str(gamedata['Road'][p][1]),
                           str((hometoi - gamedata['Road'][p][2]) / 3600), str(homeca - gamedata['Road'][p][0]),
                           str(homecf - gamedata['Road'][p][1]),
                           str(gamedata['Road'][p][3]), str(gamedata['Road'][p][4]),
                           str(homega - gamedata['Road'][p][3]),
                           str(homegf - gamedata['Road'][p][4]),
                           str(gamedata['Road'][p][5]), str(gamedata['Road'][p][6]), str(gamedata['Road'][p][7]),
                           str(gamedata['Road'][p][8]), str(gamedata['Road'][p][9])]
                    w.write('\n{0:s}'.format(','.join(lst)))
                except KeyError:
                    if not p[0] == '#':
                        print(season, game, hname, rname, hname+p)
                    #print([key for key in posmap.keys() if key[:3] == hname])
                    #print([key for key in posmap.keys() if key[:3] == rname])
                    #raise KeyError
        except IndexError as e:
            print(season, game, e, e.args)
    w.close()
    print('Done generating game-by-game for', season)

def read_toi_rates(season, by_team=True):
    """Returns {team: {name: min off (in mins)}} if by_team=True
    else, returns {name: min off}
    """
    reader = open(get_gamebygame_data_filename(season), 'r')
    reader.readline()
    toion = {}
    toioff = {}
    while True:
        try:
            line2 = reader.readline().rstrip().split(',')
            team = line2[0]
            name = line2[1]
            pos = line2[2]
            gp = int(line2[3])
            minon = float(line2[4])
            minoff = float(line2[5])
            if by_team:
                if team not in toion:
                    toion[team] = {}
                    toioff[team] = {}
                if name in toion[team]:
                    toioff[team][name] += minoff
                    toion[team][name] += minon
                else:
                    toioff[team][name] = minoff
                    toion[team][name] = minon
            else:
                if name in toion:
                    toioff[name] += minoff
                    toion[name] += minon
                else:
                    toioff[name] = minoff
                    toion[name] = minon
        except Exception as e:
            break
    reader.close()
    toi60 = {}
    if by_team:
        for team in toion:
            toi60[team] = {toion[team][p]/(toion[team][p]+toioff[team][p]) for p in toion[team]}
    else:
        toi60 = {toion[p]/(toion[p] + toioff[p])*60 for p in toion}
    return toion, toioff, toi60

def get_penalty_type(info):
    """Gets penalty type"""
    if 'v' in info[3] or ':' in info[4]:
        info[11] = info[11].lower()
        if '-' in info[11]:
            if not 'hi-stick' in info[11] and not 'ps' in info[11]:
                info[11] = info[11][:info[11].index('-')].strip()
        if '(' in info[11]:
            info[11] = info[11][:info[11].index('(')].strip()
        info[11] = info[11].lower()
        if info[11] in ['hi stick', 'hi-sticking']:
            return 'high-sticking'
        elif info[11] == 'face':
            return 'faceoff violation'
        elif info[11] == 'delaying game':
            return 'delay of game'
        elif info[11] == 'embellishment':
            return 'diving'
        return info[11].lower()
    elif 'v' in info[1] or ':' in info[2]:
        info[9] = info[9].lower()
        if '-' in info[9]:
            if not 'hi-stick' in info[9] and not 'ps' in info[9]:
                info[9] = info[9][:info[9].index('-')].strip()
        if '(' in info[9]:
            info[9] = info[9][:info[9].index('(')].strip()
        info[9] = info[9].lower()
        if info[9] in ['hi stick', 'hi-sticking']:
            return 'high-sticking'
        elif info[9] == 'face':
            return 'faceoff violation'
        elif info[9] == 'delaying game':
            return 'delay of game'
        elif info[9] == 'embellishment':
            return 'diving'
        return info[9].lower()

def get_number_dict(season, game):
    """Matches player names and numbers"""
    hdct = {}
    rdct = {}
    for line in read_game_corsi(season, game):
        for p in get_home_players(line):
            p = p.lower()
            first, last = p.split(' ', 1)
            hdct[p] = last
            if last in hdct:
                hdct[last].add(p)
            else:
                hdct[last] = {p}

        for p in get_road_players(line):
            p = p.lower()
            first, last = p.split(' ', 1)
            rdct[p] = last
            if last in rdct:
                rdct[last].add(p)
            else:
                rdct[last] = {p}
    return hdct, rdct

def match_name(p_org, num_name_dict):
    """For matching e.g. #40 Zetterberg, 40 Zetterberg, or Zetterberg to Henrik Zetterberg"""
    if p_org == '#team':
        return 'team'
    elif p_org == 'n/a':
        return 'n/a'
    elif p_org in num_name_dict:
        return p_org
    #have to force-match when one team has two players who share a last name
    force_match = {'#22 sedin': 'daniel sedin', '#33 sedin': 'henrik sedin',
                  '#11 staal': 'jordan staal', '#12 staal': 'eric staal',
                  '#18 staal': 'marc staal',
                  '#25 hamilton': 'freddie hamilton', '#27 hamilton': 'dougie hamilton',
                  "#90 o'reilly": "ryan o'reilly", "#19 o'reilly": "cal o'reilly",
                  '#14 benn': 'jamie benn', '#24 benn': 'jordie benn',
                  '#10 schenn': 'brayden schenn', '#22 schenn': 'luke schenn',
                  '#86 miller': 'kevan miller', '#48 miller': 'colin miller',
                  '#28 moore': 'dominic moore', '#17 moore': 'john moore',
                  '#19 schultz': 'justin schultz', '#15 schultz': 'nick schultz',
                  '#54 jones': 'david jones', '#19 jones': 'blair jones',
                  '#26 st louis': 'martin st. louis'}
    matched = p_org
    if matched[0] == '#':
        matched = matched[matched.index(' ')+1:]
    else:
        try:
            num = int(matched[:2].strip()) #to see if the player has a number with no '#'
            matched = matched[matched.index(' ')+1:]
        except ValueError:
            pass
    try:
        matched = num_name_dict[matched.lower()]
    except Exception as e:
        if p_org in force_match:
            return force_match[p_org]
        raise e
    if len(matched) == 1:
        for p in matched:
            return p
    if len(matched) == 2:
        if p_org in force_match:
            p = force_match[p_org]
            return p
        else:
            print(p_org, matched)
