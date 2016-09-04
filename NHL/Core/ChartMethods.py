import PbPMethods2 as pm2
import GetPbP

def size_function(x):
    """Helper method for usage_chart. Returns area of bubble corresponding to this toi/60"""
    if x <= 5:
        return 0
    return 5 * (x - 5) ** 2

def usage_chart(season, team, pos=['F', 'D'], startgame=20001, endgame=21230, minimum=100, hr='both',
                bubblecolor='zs', update_data=False, sig='me', save_file=None):
    """Makes a scatterplot of F and D toicomp for players for the team in question.
    Minimum = minimum minutes on-ice for inclusion. hr='home', 'road', or 'both'.
    Bubble size TOI, bubble color ZS%
    If games have been played since toi60 calculated, set update_toi60 to True"""

    if update_data:
        pm2.gen_gamebygame(season)
    hr = hr.lower()
    home = True
    road = True
    if hr == 'road':
        home = False
    elif hr == 'home':
        road = False
    f_tot = {}
    f_n = {}
    d_tot = {}
    d_n = {}
    toion, toioff, toi60 = pm2.read_toi_rates(season)
    for sec in pm2.read_team_toi(team, season):
        g = pm2.get_game(sec)
        if startgame <= g <= endgame:
            if '@' in sec[1] and road or '@' not in sec[1] and home:
                oppteam = sec[1][-3:]
                oppf = pm2.get_road_players(sec, ['F'])
                oppd = pm2.get_road_players(sec, ['D'])
                players = pm2.get_home_players(sec, pos)
                try:
                    ftot = sum([toi60[oppteam][p] for p in oppf])
                    fn = len(oppf)
                    dtot = sum([toi60[oppteam][p] for p in oppd])
                    dn = len(oppd)
                    for p in players:
                        if p not in f_tot:
                            f_tot[p] = 0
                            f_n[p] = 0
                            d_tot[p] = 0
                            d_n[p] = 0
                            #toi[p] = 0
                        f_tot[p] += ftot
                        f_n[p] += fn
                        d_tot[p] += dtot
                        d_n[p] += dn
                        #toi[p] += 1
                except KeyError:
                    print('Cannot find {0:s} in {1:s} TOI/60 ({2:d} {3:d})'.format(p, oppteam, season, g))
        elif g > endgame:
            break
    ozs = {}
    nzs = {}
    dzs = {}
    for line in pm2.read_team_pbp(team, season, types=['FAC']):
        g = pm2.get_game(line)
        if startgame <= g <= endgame:
            if '@' in line[1] and road or '@' not in line[1] and home:
                players = pm2.get_home_players(line, pos)
                zone = pm2.get_event_zone(line)
                for p in players:
                    if p not in ozs:
                        ozs[p] = 0
                        nzs[p] = 0
                        dzs[p] = 0
                    if zone == 'Off':
                        ozs[p] += 1
                    elif zone == 'Neu':
                        nzs[p] += 1
                    elif zone == 'Def':
                        dzs[p] += 1
    cf = {}
    ca = {}
    cfoff = {}
    caoff = {}
    thisgame = None
    thisgamecf = {}
    thisgameca = {}
    thisgametotcf = 0
    thisgametotca = 0
    for line in pm2.read_team_pbp(team, season, types=['GOAL', 'SHOT', 'MISS', 'BLOCK']):
        g = pm2.get_game(line)
        if startgame <= g <= endgame:
            if '@' in line[1] and road or '@' not in line[1] and home:
                if thisgame is None:
                    thisgamecf = {}
                    thisgameca = {}
                    thisgametotcf = 0
                    thisgametotca = 0
                    thisgame = g
                if not thisgame == g:
                    for p in thisgamecf:
                        if p not in cf:
                            cf[p] = 0
                            ca[p] = 0
                            cfoff[p] = 0
                            caoff[p] = 0
                        cf[p] += thisgamecf[p]
                        ca[p] += thisgameca[p]
                        cfoff[p] += thisgametotcf - thisgamecf[p]
                        caoff[p] += thisgametotca - thisgameca[p]
                    thisgamecf = {}
                    thisgameca = {}
                    thisgametotcf = 0
                    thisgametotca = 0
                    thisgame = g
                players = pm2.get_home_players(line, pos)
                if pm2.get_acting_team(line) == team:
                    thisgametotcf += 1
                    for p in players:
                        if p not in thisgamecf:
                            thisgamecf[p] = 0
                            thisgameca[p] = 0
                        thisgamecf[p] += 1
                else:
                    thisgametotca += 1
                    for p in players:
                        if p not in thisgameca:
                            thisgamecf[p] = 0
                            thisgameca[p] = 0
                        thisgameca[p] += 1
    for p in thisgamecf:
        if p not in cf:
            cf[p] = 0
            ca[p] = 0
            cfoff[p] = 0
            caoff[p] = 0
        cf[p] += thisgamecf[p]
        ca[p] += thisgameca[p]
        cfoff[p] += thisgametotcf - thisgamecf[p]
        caoff[p] += thisgametotca - thisgameca[p]

    cfon60 = {}
    cfoff60 = {}
    cfrel60 = {}
    toion, toioff, toi60 = pm2.read_toi_rates(season)
    for p in cf:
        try:
            cfon60[p] = (cf[p] - ca[p]) / (toion[team][p] / 60)
            cfoff60[p] = (cfoff[p] - caoff[p]) / (toioff[team][p] / 60)
            cfrel60[p] = cfon60[p] - cfoff60[p]
        except KeyError:
            print('{0:s} not found for {1:s}'.format(p, team))
    toi2 = {}
    for p in toion[team]:
        if toion[team][p] >= minimum:
            toi2[p] = toion[team][p]
    zs = {}
    for p in toi2:
        if p not in ozs:
            zs[p] = .5
        else:
            zs[p] = ozs[p] / (ozs[p] + dzs[p])

    plist = [p for p in toi2]
    fcomp = [f_tot[p] / f_n[p] for p in plist]
    dcomp = [d_tot[p] / d_n[p] for p in plist]

    areas = [size_function(toi60[team][p]) for p in plist]
    if bubblecolor == 'zs':
        colors = [2 * (zs[p] - 0.5) for p in plist]
    else:
        colors = [cfrel60[p] for p in plist]

    import matplotlib.pyplot as plt

    plt.clf()

    if sig == 'me':
        me = '@muneebalamcu'
    elif sig == 'japers':
        me = "@JapersRink"

    if home and not road:
        plt.title(
            'Usage chart for {0:d}-{2:d} {1:s} at home'.format(season, team,
                                                               (season + 1) - 2000))
    elif road and not home:
        plt.title(
            'Usage chart for {0:d}-{2:d} {1:s} on road'.format(season, team,
                                                               (season + 1) - 2000))
    else:
        plt.title('Usage chart for {0:d}-{2:d} {1:s}'.format(season, team,
                                                             (season + 1) - 2000))
    plt.xlabel('D QualComp (TOI/60)')
    plt.ylabel('F QualComp (TOI/60)')
    plt.scatter(dcomp, fcomp, s=areas, c=colors, cmap=plt.cm.coolwarm, alpha=0.5)
    for i in range(len(plist)):
        plt.annotate(plist[i], xy=(dcomp[i], fcomp[i]), ha='center', va='center')

    plt.grid(b=True, which='major', axis='y', linestyle='-')
    plt.grid(b=True, which='minor', axis='y', linestyle=':')
    plt.minorticks_on()
    plt.grid(b=True, which='major', axis='x', linestyle='-')
    plt.grid(b=True, which='minor', axis='x', linestyle=':')

    start = min(colors)
    end = max(colors)
    step = (end - start) / 5
    if bubblecolor == 'zs':
        tick_places = [start + step * n for n in range(6)]
        tick_vals = ['{0:d}%'.format(int((x / 2 + 0.5) * 100)) for x in tick_places]
        cbar = plt.colorbar(orientation='vertical', fraction=0.05, ticks=tick_places)
        cbar.ax.set_yticklabels(tick_vals)
        cbar.set_label('OZ / (OZ+DZ)')
    else:
        cbar = plt.colorbar(orientation='vertical', fraction=0.05)
        cbar.set_label('Relative SAT / 60')
    if sig is not None:
        cbar.ax.set_xlabel(me, labelpad=20)

    l1 = plt.scatter([], [], s=size_function(12), edgecolors='none', alpha=0.5)
    l2 = plt.scatter([], [], s=size_function(16), edgecolors='none', alpha=0.5)
    l3 = plt.scatter([], [], s=size_function(20), edgecolors='none', alpha=0.5)
    labels = ['12', '16', '20']
    plt.legend([l1, l2, l3], labels, ncol=3, loc=4, labelspacing=1, borderpad=0.7, title='TOI/60', scatterpoints=1,
               scatteryoffsets=[1], framealpha=0.5)
    if save_file is None:
        plt.show()
    else:
        plt.savefig(save_file)
    plt.clf()

def h2h_charts(season, games, save_folder=None, strengths=['5v5'], bigchart=True):
    if not isinstance(games, list):
        games = [games]
    (hname, rname), (horder, rorder), (hnumbers, rnumbers), (homecf, roadcf), (hcorsi, rcorsi), h2hcf, \
    (hwhcf_h, hwhcf_r), (htotalstoi, rtotalstoi), h2htoi, (hwhtoi_h, hwhtoi_r), \
    num_fs = pm2.h2h_chart_data(season, games, strengths)

    brangey = [i - 0.5 for i in range(len(horder) + 1)]
    brangex = [i - 0.5 for i in range(len(rorder) + 1)]

    cdstr = homecf - roadcf
    if cdstr > 0:
        cdstr = '+{0:d}'.format(cdstr)
    elif cdstr == 0:
        cdstr = 'even'
    cdstr = str(cdstr)
    cdstr2 = roadcf - homecf
    if cdstr2 > 0:
        cdstr2 = '+{0:d}'.format(cdstr2)
    elif cdstr2 == 0:
        cdstr2 = 'even'
    cdstr2 = str(cdstr2)
    gamestr = ', '.join([str(x) for x in games])

    if len(games) == 1:
        interteam_title = '{0:s} at {1:s} ({5:s}) H2H TOI and Corsi\n{2:d}-{3:s} Game {4:d}'.format(
            GetPbP.get_mascot_name(rname),
            GetPbP.get_mascot_name(hname),
            season, str(season + 1)[2:], games[0], cdstr)
        interteam_file = '{0:s}{1:d}0{2:d} {3:s}@{4:s}.png'.format(save_folder, season, games[0],
                                                                   GetPbP.get_mascot_name(rname),
                                                                   GetPbP.get_mascot_name(hname))
    else:
        interteam_title = '{0:s} vs {1:s} ({5:s}) H2H TOI and Corsi\n{2:d}-{3:s} Games {4:s}'.format(
            GetPbP.get_mascot_name(rname),
            GetPbP.get_mascot_name(hname),
            season, str(season + 1)[2:], gamestr, cdstr)
        interteam_file = '{0:s}{1:d}0{2:s} {3:s} vs {4:s}.png'.format(save_folder, season, '[Multi]',
                                                                   GetPbP.get_mascot_name(rname),
                                                                   GetPbP.get_mascot_name(hname))

    general_h2h_chart(h2htoi, h2hcf, hcorsi, rcorsi, htotalstoi, rtotalstoi, brangex,
                      brangey, hname, horder, hnumbers, rname, rorder, rnumbers, num_fs, interteam_title,
                      interteam_file, bigchart)

    if len(games) == 1:
        hteam_title = '{0:s} ({4:s}) H2H TOI and Corsi\n{1:d}-{2:s} Game {3:d}'.format(GetPbP.get_mascot_name(hname),
                                                                                       season, str(season + 1)[2:],
                                                                                       games[0], cdstr)
        rteam_title = '{0:s} ({4:s}) H2H TOI and Corsi\n{1:d}-{2:s} Game {3:d}'.format(GetPbP.get_mascot_name(rname),
                                                                                       season, str(season + 1)[2:],
                                                                                       games[0], cdstr2)
        hteam_file = '{0:s}{1:d}0{2:d} {3:s}.png'.format(save_folder, season, games[0], GetPbP.get_mascot_name(hname))
        rteam_file = '{0:s}{1:d}0{2:d} {3:s}.png'.format(save_folder, season, games[0], GetPbP.get_mascot_name(rname))
    else:
        hteam_title = '{0:s} ({4:s}) H2H TOI and Corsi\n{1:d}-{2:s} Games {3:s}'.format(GetPbP.get_mascot_name(hname),
                                                                                       season, str(season + 1)[2:],
                                                                                       gamestr, cdstr)
        rteam_title = '{0:s} ({4:s}) H2H TOI and Corsi\n{1:d}-{2:s} Games {3:s}'.format(GetPbP.get_mascot_name(rname),
                                                                                       season, str(season + 1)[2:],
                                                                                       gamestr, cdstr2)
        hteam_file = '{0:s}{1:d}0{2:s} {3:s}.png'.format(save_folder, season, '[Multi]', GetPbP.get_mascot_name(hname))
        rteam_file = '{0:s}{1:d}0{2:s} {3:s}.png'.format(save_folder, season, '[Multi]', GetPbP.get_mascot_name(rname))

    general_h2h_chart(hwhtoi_h, hwhcf_h, hcorsi, hcorsi, htotalstoi, htotalstoi, brangey,
                      brangey, hname, horder, hnumbers, hname, horder[::-1], hnumbers, (num_fs[0], num_fs[0]), hteam_title,
                      hteam_file, bigchart)
    general_h2h_chart(hwhtoi_r, hwhcf_r, rcorsi, rcorsi, rtotalstoi, rtotalstoi, brangex,
                      brangex, rname, rorder[::-1], rnumbers, rname, rorder, rnumbers, (num_fs[1], num_fs[1]), rteam_title,
                      rteam_file, bigchart)

    print('Done with H2H for', season, gamestr)


def general_h2h_chart(h2htoi, h2hcorsi, hcorsi, rcorsi, htotalstoi, rtotalstoi, brangex, brangey, hname,
                      hnameorder, hnumbers, rname, rnameorder, rnumbers, num_fs, save_title, save_file=None,
                      bigchart=False):
    import matplotlib.pyplot as plt

    toiy = []
    toix = []
    weights = []
    for p1 in range(len(hnameorder)):
        for p2 in range(len(rnameorder)):
            toix.append(p2)
            toiy.append(p1)
            if rnameorder[p2] not in h2htoi[hnameorder[p1]]:
                weights.append(0)
            else:
                weights.append(h2htoi[hnameorder[p1]][rnameorder[p2]])
    if bigchart:
        fig = plt.figure(figsize=[10.5, 7])
    plt.hist2d(toix, toiy, bins=[brangex, brangey], weights=weights, cmap=plt.cm.summer)
    plt.yticks([i for i in range(len(hnameorder))],
               ['{0:d} {1:s}'.format(hnumbers[hnameorder[i]], ' '.join(hnameorder[i].split(' ')[1:]))
                for i in range(len(hnameorder))], fontsize=10)
    plt.ylabel('{0:s}'.format(GetPbP.get_mascot_name(hname)), labelpad=0)
    plt.xticks([i for i in range(len(rnameorder))],
               ['{0:d} {1:s}'.format(rnumbers[rnameorder[i]], ' '.join(rnameorder[i].split(' ')[1:]))
                for i in range(len(rnameorder))], fontsize=10, rotation=45, ha='right')
    plt.xlabel('{0:s}'.format(GetPbP.get_mascot_name(rname)), labelpad=0)
    plt.ylim(brangey[0], brangey[-1])
    plt.xlim(brangex[0], brangex[-1])

    for tic in plt.gca().xaxis.get_major_ticks():
        tic.tick1On = tic.tick2On = False
    for tic in plt.gca().yaxis.get_major_ticks():
        tic.tick1On = tic.tick2On = False

    cbar = plt.colorbar(pad=0.1)
    cbar.ax.set_yticklabels(['{0:.1f}'.format(int(time.get_text()) / 60) for time in cbar.ax.get_yticklabels()])
    cbar.ax.set_ylabel('TOI (min)')
    cbar.ax.set_xlabel('Muneeb Alam\n@muneebalamcu', labelpad=20)
    c = 'k'
    for i in range(max(len(hnameorder), len(rnameorder)) + 1):
        x = [brangex[0], brangex[-1]]
        y = [i - 0.5, i - 0.5]
        plt.plot(x, y, color=c)
        x = [brangey[0], brangey[-1]]
        y = [i - 0.5, i - 0.5]
        plt.plot(y, x, color=c)
    plt.plot([brangex[0], brangex[-1]],
             [len(hnameorder) - num_fs[0] - 0.5, len(hnameorder) - num_fs[0] - 0.5],
             color=c, linewidth=2)
    plt.plot([num_fs[1] - 0.5, num_fs[1] - 0.5], [brangey[0], brangey[-1]], color=c, linewidth=2)

    neg_x = []
    neg_y = []

    for i2 in range(len(hnameorder)):
        p1 = hnameorder[i2]
        for i1 in range(len(rnameorder)):
            p2 = rnameorder[i1]
            try:
                diff = h2hcorsi[p1][p2]
            except KeyError:
                diff = 0
            if diff > 0:
                annotation = '+{0:.0f}'.format(diff)
            elif diff == 0:
                annotation = '{0:.0f}'.format(diff)
            else:
                annotation = '{0:.0f}'.format(diff)
                neg_x.append(i1)
                neg_y.append(i2)
            plt.annotate(annotation, xy=(i1, i2), xytext=(i1, i2), fontsize=8, ha='center', va='center')

    bubble_title = '{0:s}\nCF - CA'.format(GetPbP.get_mascot_name(hname))
    plt.annotate(bubble_title, xy=(0, len(hnameorder) - 0.75), xytext=(-3, len(hnameorder) + 2),
                 annotation_clip=False, ha='center', va='top',
                 fontsize=10, bbox=dict(boxstyle="round", fc=(1.0, 0.7, 0.7), ec="none"),
                 arrowprops=dict(arrowstyle="->"))
    plt.scatter(neg_x, neg_y, marker='o', edgecolors='k', s=200, facecolors='none')

    ax1 = plt.twiny()
    ticks = [rtotalstoi[rnameorder[i]] for i in range(len(rnameorder))]
    for i in range(len(ticks)):
        if rcorsi[rnameorder[i]] > 0:
            ticks[i] = '{0:.1f}, +{1:.0f}'.format(ticks[i] / 60, rcorsi[rnameorder[i]])
        else:
            ticks[i] = '{0:.1f}, {1:.0f}'.format(ticks[i] / 60, rcorsi[rnameorder[i]])
    ax1.set_xticks([x + 0.5 for x in brangex])  # to center labels
    ax1.set_xticklabels(ticks, fontsize=8, rotation=45, ha='left')
    ax1.set_xlim(brangex[0], brangex[-1])
    ax1.set_xlabel('Total 5v5 TOI and Corsi', fontdict={'size': 10}, labelpad=0)
    for tic in ax1.xaxis.get_major_ticks():
        tic.tick1On = tic.tick2On = False
    for tic in ax1.yaxis.get_major_ticks():
        tic.tick1On = tic.tick2On = False

    ax2 = plt.twinx()
    ticks2 = [htotalstoi[hnameorder[i]] for i in range(len(hnameorder))]
    for j in range(len(ticks2)):
        if hcorsi[hnameorder[j]] > 0:
            ticks2[j] = '{0:.1f}, +{1:.0f}'.format(ticks2[j] / 60, hcorsi[hnameorder[j]])
        else:
            ticks2[j] = '{0:.1f}, {1:.0f}'.format(ticks2[j] / 60, hcorsi[hnameorder[j]])
    ax2.set_yticks([i for i in range(len(hnameorder))])
    ax2.set_yticklabels(ticks2, fontsize=8)
    ax2.set_ylim(brangey[0], brangey[-1])
    for tic in ax2.xaxis.get_major_ticks():
        tic.tick1On = tic.tick2On = False
    for tic in ax2.yaxis.get_major_ticks():
        tic.tick1On = tic.tick2On = False

    plt.subplots_adjust(bottom=0.18)
    plt.subplots_adjust(left=0.15)
    plt.subplots_adjust(top=0.80)
    plt.subplots_adjust(right=1.0)
    plt.title(save_title, y=1.2)
    plt.tight_layout()
    if save_file is None:
        plt.show()
    else:
        plt.savefig(save_file)
    plt.clf()

def plot_pp_units(team, seasons, strength=['5v4'], save_file=None):

    if not isinstance(seasons, list):
        seasons = [seasons]
    if not isinstance(strength, list):
        strength = [strength]

    #get all shots for
    sf = []
    for season in seasons:
        for line in pm2.read_team_pbp(team, season, types=['GOAL', 'SHOT', 'MISS'], strengths=strength):
            if pm2.get_acting_team(line) == team:
                if pm2.get_location(line)[0] is not None:
                    sf.append(line)

    #find the most common two 5v4 unit
    units = {} #{ (players): toi}
    for season in seasons:
        for line in pm2.read_team_toi(team, season, ['5v4']):
            ps = pm2.get_home_players(line)
            ps.sort()
            ps = tuple(ps)
            if ps not in units:
                units[ps] = 0
            units[ps] += 1
    topfour = set()
    topfourlst = []
    for i in range(2):
        maxunit = None
        for unit, toi in units.items():
            if unit not in topfour and (maxunit is None or units[maxunit] < units[unit]):
                maxunit = unit
        topfour.add(maxunit)
        topfourlst.append(maxunit)

    #find each player's shot center for the top unit
    import matplotlib.pyplot as plt
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 12
    fig_size[1] = 6
    plt.rcParams["figure.figsize"] = fig_size
    rink_background()

    playershots1 = {}
    playershots2 = {}
    for line in sf:
        ps = pm2.get_home_players(line)
        ps.sort()
        ps = tuple(ps)
        if ps == topfourlst[0]:
            shooter = pm2.get_acting_player(line)
            if shooter not in playershots1:
                playershots1[shooter] = []
            loc = pm2.get_location(line)
            if loc[0] < 0:
                loc = (-1 * loc[0], -1 * loc[1])
            playershots1[shooter].append((-1 * loc[0], -1 * loc[1]))
        elif ps == topfourlst[1]:
            shooter = pm2.get_acting_player(line)
            if shooter not in playershots2:
                playershots2[shooter] = []
            loc = pm2.get_location(line)
            if loc[0] < 0:
                loc = (-1 * loc[0], -1 * loc[1])
            playershots2[shooter].append((loc[0], loc[1]))
    playercenters1 = {}
    playercenters2 = {}
    for p, shots in playershots1.items():
        playercenters1[p] = centroid(shots, True)
    for p, shots in playershots2.items():
        playercenters2[p] = centroid(shots, True)
    colors = ['r', 'g', 'y', 'b', 'k']
    for c, p in enumerate(topfourlst[0]):
        plt.scatter([x for x, y in playershots1[p]], [y for x, y in playershots1[p]], alpha=0.5, color=colors[c])
        plt.scatter([playercenters1[p][0]], [playercenters1[p][1]], color=colors[c], marker='d', s=200, edgecolor='k')
    for c, p in enumerate(topfourlst[1]):
        plt.scatter([x for x, y in playershots2[p]], [y for x, y in playershots2[p]], alpha=0.5, color=colors[c])
        plt.scatter([playercenters2[p][0]], [playercenters2[p][1]], color=colors[c], marker='d', s=200, edgecolor='k')

    for p in topfourlst[0]:
        plt.annotate('{0:s}\n{1:d} SOG'.format(p.split(' ', 1)[1], len(playershots1[p])), xy=playercenters1[p],
                     xytext=(playercenters1[p][0], playercenters1[p][1] + 3),
                     ha='center', va='bottom', fontsize=10)
    for p in topfourlst[1]:
        plt.annotate('{0:s}\n{1:d} SOG'.format(p.split(' ', 1)[1], len(playershots2[p])), xy=playercenters2[p],
                     xytext=(playercenters2[p][0], playercenters2[p][1] + 3),
                     ha='center', va='bottom', fontsize=10)
    title = 'Shot locations for {0:s} top two 5v4 units {1:s}'.format(team, ', '.join([str(x) for x in seasons]))
    title += '\nLeft: {0:s} ({1:d} min)\nRight: {2:s} ({3:d} min)'.format(
        ', '.join([name.split(' ', 1)[1] for name in topfourlst[0]]),
        round(units[topfourlst[0]]/60),
        ', '.join([name.split(' ', 1)[1] for name in topfourlst[1]]),
        round(units[topfourlst[1]]/60))
    plt.title(title, y=0.95)
    plt.xticks([])
    plt.yticks([])
    plt.axis('off')
    plt.gcf().tight_layout()
    if save_file is None:
        plt.show()
    else:
        plt.savefig(save_file)
    plt.clf()

def rink_background(which='hfull'):
    """Choose from hfull (horiz-full), vfull, right, left, up, or down"""

    import matplotlib.pyplot as plt

    if which=='hfull':
        img = plt.imread(pm2.get_full_rink_filename())
        implot = plt.imshow(img, extent=[-100, 100, -45, 45])
    elif which=='vfull':
        img = plt.imread(pm2.get_full_rink_filename(orientation='vertical'))
        implot = plt.imshow(img, extent=[-45, 45, -100, 100])
    elif which=='top':
        img = plt.imread(pm2.get_bottom_rink_filename())
        implot = plt.imshow(img, extent=[-45, 45, 0, 100], origin='upper')
    elif which=='bottom':
        img = plt.imread(pm2.get_bottom_rink_filename())
        implot = plt.imshow(img, extent=[-45, 45, -100, 0])
    elif which=='left':
        img = plt.imread(pm2.get_left_rink_filename())
        implot = plt.imshow(img, extent=[-100, 0, -45, 45])
    elif which=='right':
        img = plt.imread(pm2.get_left_rink_filename())
        import numpy as np
        img = np.fliplr(img)
        implot = plt.imshow(img, extent=[0, 100, -45, 45])


def plot_game_shots(season, game):
    """Plots 5v5 shots from given game on rink"""

    import matplotlib.pyplot as plt

    rink_background()

    coors = pm2.get_game_shot_locations(season, game, types=['GOAL'])
    xs = [shot[0] for shot in coors if shot[0] is not None]
    ys = [shot[1] for shot in coors if shot[1] is not None]
    plt.scatter(xs, ys, color='k', label='Goal')

    coors = pm2.get_game_shot_locations(season, game, types=['SHOT'])
    xs = [shot[0] for shot in coors if shot[0] is not None]
    ys = [shot[1] for shot in coors if shot[1] is not None]
    plt.scatter(xs, ys, color='c', label='Save')

    plt.legend(loc='center', scatterpoints=1)

    plt.show()

def get_team_shot_locations(team, season, types=['GOAL', 'SHOT'], strengths=['5v5'], players_on=None, states=['all'],
                            against=False, players_off=None):
    """Returns x, y, goal?, shooter tuples for shot locations for team in season."""

    locs = []
    for line in pm2.read_team_pbp(team, season, types, strengths, states, players_on, players_off=players_off):
        if not against and (pm2.get_acting_team(line) == team) or against and (pm2.get_acting_team(line) != team):
            loc = pm2.get_location(line)
            goal = pm2.get_event_type(line) == 'GOAL'
            shooter = pm2.get_acting_player(line)
            if not against and loc[0] is not None and loc[0] > 0 or against and loc[0] is not None and loc[0] < 0:
                #only OZ for SF and DZ for SA
                locs.append((loc[0], loc[1], goal, shooter))
    return locs


def plot_team_shots(team, seasons, strengths=['5v5'], players_on=None, show_centers=0, scale=True, against=False,
                    players_off=None, code_by_player=False, force_colors=None, force_markers=None):
    #plots SOG and goals as well as show_centers # of shot centroids on RHS (via kmeans).
    # Scale scales marker size by % of tot SOG or goals if show_centers > 0
    #code by player-->finds players who scored goals, color-codes shot chart with those players + other
    if not isinstance(seasons, list):
        seasons = [seasons]
    if players_on is not None and not isinstance(players_on, list):
        players_on = [players_on]
    if players_off is not None and not isinstance(players_off, list):
        players_off = [players_off]

    import matplotlib.pyplot as plt
    from operator import itemgetter

    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 12
    fig_size[1] = 6
    plt.rcParams["figure.figsize"] = fig_size
    rink_background()

    coors = []
    coors2 = []
    for yr in seasons:
        coors += get_team_shot_locations(team, yr, ['GOAL', 'SHOT', 'MISS'], strengths, players_on, against=against,
                                         players_off=players_off)
        coors2 += get_team_shot_locations(team, yr, ['GOAL'], strengths, players_on, against=against,
                                          players_off=players_off)
    xs = [shot[0] * -1 for shot in coors]
    ys = [shot[1] * -1 for shot in coors]
    xs2 = [x * -1 for x in xs]
    ys2 = [y * -1 for y in ys]
    goal = tuple([i for i in range(len(coors)) if coors[i][2]])
    shooters = [shot[3] for shot in coors]
    ngoals = sum([1 if g else 0 for g in goal])
    gset = set(goal)
    nshots = len(xs2)

    shot_volume = {}

    shot_volume = {p: 0 for p in set(shooters)}

    for x, y, p in zip(xs, ys, shooters):
        if p not in shot_volume:
            shot_volume[p] = 0
        shot_volume[p] += 1
    top5 = set()
    for i in range(5):
        maxval = None
        for p in shot_volume:
            if p not in top5 and (maxval is None or shot_volume[p] > shot_volume[maxval]):
                maxval = p
        top5.add(maxval)

    xy_by_shooter = {p: [[], []] for p in top5}
    xy_by_shooter['Other'] = [[], []]
    for x, y, p in zip(xs, ys, shooters):
        p2 = p
        if p2 not in xy_by_shooter:
            p2 = 'Other'
        xy_by_shooter[p2][0].append(-1 * x)
        xy_by_shooter[p2][1].append(-1 * y)

    if code_by_player:
        colorlst = ['r', 'c', 'lightgreen', 'orange', 'b', 'k']
        markerlst = ['o', 'v', '*', 's', 'h', '+']

        if force_colors is None or 'Other' not in force_colors:
            color = colorlst[-1]
        else:
            color = force_colors['Other']

        if force_markers is None or 'Other' not in force_markers:
            marker = markerlst[-1]
        else:
            marker = force_markers['Other']
        plt.scatter(xy_by_shooter['Other'][0], xy_by_shooter['Other'][1], color=color, label='Other', alpha=0.5,
                    marker=marker, s=40)
        del xy_by_shooter['Other']
        for i, p in enumerate(xy_by_shooter.keys()):
            if force_colors is None or p not in force_colors:
                color = colorlst[i]
            else:
                color = force_colors[p]

            if force_markers is None or p not in force_markers:
                marker = markerlst[i]
            else:
                marker = force_markers[p]
            plt.scatter(xy_by_shooter[p][0], xy_by_shooter[p][1], color=color, label=p, alpha=0.5,
                        marker=marker, s=40)
        plt.legend(loc='center', scatterpoints=1, title='Shooter Key', fontsize=11)
        plt.scatter(itemgetter(*goal)(xs), itemgetter(*goal)(ys), color='lightgreen', label='Goal', alpha=0.5)
    else:
    #plot on left side
        plt.scatter(itemgetter(*goal)(xs), itemgetter(*goal)(ys), color='lightgreen', label='Goal', alpha=0.5)

        #plot on right side
        plt.scatter(xs2, ys2, color='c', label='Shot', alpha=0.5)
        plt.legend(loc='center', scatterpoints=1)

    if show_centers > 0:
        shots_for = [(xs2[i], ys2[i]) for i in range(len(xs))]
        from sklearn.cluster import KMeans
        kmeans_sog = KMeans(n_clusters=show_centers)
        kmeans_sog.fit_predict(shots_for)
        xs = [tup[0] for tup in kmeans_sog.cluster_centers_]
        ys = [tup[1] for tup in kmeans_sog.cluster_centers_]
        frac = [0 for tup in kmeans_sog.cluster_centers_]
        for num in kmeans_sog.labels_:
            frac[num] += 1
        goal_by_cluster = [0 for tup in kmeans_sog.cluster_centers_]
        for i in range(len(kmeans_sog.labels_)):
            if i in gset:
                goal_by_cluster[kmeans_sog.labels_[i]] += 1
        shpct = ['{0:d} sh%'.format(round(100*goal_by_cluster[i]/frac[i])) for i in range(len(frac))]

        tot = len(kmeans_sog.labels_)
        for i in range(len(frac)):
            frac[i] = '{0:d}%'.format(round(100*frac[i]/tot))
        plt.scatter(xs, ys, color='k', marker='D', s=100)
        for i in range(len(frac)):
            plt.annotate('{0:s}\n{1:s}'.format(frac[i], shpct[i]), xy=(xs[i], ys[i]), xytext=(xs[i]-7, ys[i]), ha='center', va='center')

        kmeans_g = KMeans(n_clusters=show_centers)
        kmeans_g.fit_predict([tup[:2] for tup in coors2])
        xs = [tup[0] * -1 for tup in kmeans_g.cluster_centers_]
        ys = [tup[1] * -1 for tup in kmeans_g.cluster_centers_]
        #plot on left side
        frac = [0 for tup in kmeans_g.cluster_centers_]
        for num in kmeans_g.labels_:
            frac[num] += 1
        tot = len(kmeans_g.labels_)
        for i in range(len(frac)):
            frac[i] = '{0:d}%'.format(round(100*frac[i]/tot))
        plt.scatter(xs, ys, color='darkgreen', marker='D', s=100)
        for i in range(len(frac)):
            plt.annotate(frac[i], xy=(xs[i], ys[i]), xytext=(xs[i]+7, ys[i]), ha='center', va='center')


    title = '{0:s} {2:d} goals (left) and {1:d} shots (right)'.format(team, nshots, ngoals)
    if against:
        title += ' against'
    title += ', {0:s}'.format(', '.join(strengths))
    if players_on is not None or players_off is not None:
        title += '\n'
    if players_on is not None:
        title += 'With {0:s}'.format(', '.join(players_on))
        if players_off is not None:
            title += ' and '
    if players_off is not None:
        title += 'Without {0:s}'.format(', '.join(players_off))
    title += '\n{0:s}'.format(', '.join(str(x) for x in seasons))
    plt.title(title, y=0.99)
    plt.axis('off')
    plt.gcf().tight_layout()
    plt.show()
    plt.clf()

def get_team_color(team):
    """Returns strings of color most appropriate for team. One dominant color and one secondary color"""

    team_color_dct = {'ANA': ['black', 'orange'],
                      'L.A': ['black', 'white'],
                      'S.J': ['teal', 'teal'],
                      'PHX': ['saddlebrown', 'antiquewhite'],
                      'ARI': ['saddlebrown', 'antiquewhite'],
                      'DAL': ['limegreen', 'silver'],
                      'CHI': ['red', 'black'],
                      'DET': ['red', 'linen'],
                      'NSH': ['y', 'darkblue'],
                      'STL': ['blue', 'midnightblue'],
                      'CBJ': ['darkblue', 'lightblue'],
                      'EDM': ['orange', 'blue'],
                      'CGY': ['black', 'red'],
                      'VAN': ['darkblue', 'green'],
                      'MIN': ['forestgreen', 'red'],
                      'COL': ['darkblue', 'maroon'],
                      'BOS': ['y', 'black'],
                      'MTL': ['blue', 'r'],
                      'BUF': ['navy', 'gold'],
                      'TOR': ['blue', 'white'],
                      'OTT': ['red', 'gold'],
                      'PHI': ['orange', 'black'],
                      'PIT': ['black', 'goldenrod'],
                      'N.J': ['r', 'green'],
                      'NYR': ['blue', 'red'],
                      'NYI': ['darkorange', 'blue'],
                      'FLA': ['navy', 'firebrick'],
                      'WSH': ['red', 'blue'],
                      'T.B': ['black', 'blue'],
                      'CAR': ['black', 'firebrick'],
                      'ATL': ['firebrick', 'cornflowerblue'],
                      'WPG': ['darkblue', 'silver']}

    return team_color_dct[team]


def centroid(data, remove_outliers=False):
    #data should be list of x,y tuples or similar. Outliers removes shots >= 1.5 iqr from median in any column
    from numpy import mean, array, median, percentile
    data2 = array(data)
    if remove_outliers:
        from numpy import std
        medians = median(data2, axis=0)
        q75, q25 = percentile(data2, [75, 25], axis=0)
        iqr = q75 - q25
        data3 = []
        for i in range(len(data2)):
            out = False
            for j in range(len(data2[i])):
                try:
                    if abs((data2[i][j] - medians[j])/iqr[j]) >= 1.5:
                        out = True
                        break
                except Exception as e:
                    print(data[i], e, e.args)
                    out = True
            if not out:
                data3.append(data2[i])
        return mean(array(data3), axis=0)

    return mean(array(data2), axis=0)

def rolling_penalty_breakdown(player, team, startseason, endseason=None, roll_len=20, strengths='all',
                              exclude=['misconduct', 'fighting', 'game misconduct', 'match penalty']):
    """Line graph, goes by game. Set player to None for all players. Use player number, not name.
    One graph for drawn, another for taken. Excludes fighting"""

    if endseason is None:
        endseason = startseason

    if not isinstance(strengths, list):
        strengths = [strengths]

    games = []
    obs_t = []
    obs_d = []
    disc_t = []
    disc_d = []
    agg_t = []
    agg_d = []
    other_t = []
    other_d = []
    total_pen_taken_dct = {}
    total_pen_drawn_dct = {}
    tsum = 0
    dsum = 0

    for season in range(startseason, endseason + 1):
        game = 0
        for line in pm2.read_team_pbp(season, team, types=['PENL'], strengths=strengths):
            g = pm2.get_game(line)
            if not g == game:
                game = g
                games.append(len(games) + 1)
                for lst in [obs_t, obs_d, disc_t, disc_d, agg_t, agg_d, other_t, other_d]:
                    lst.append(0)
            penl = pm2.get_penalty_type(line)
            if pm2.get_acting_team(line) == team:
                if player is None or player is [] or pm2.get_acting_player(line) == player:
                    if penl in OBS_NAMES:
                        obs_t[-1] += 1
                    elif penl in DISC_NAMES:
                        disc_t[-1] += 1
                    elif penl in AGG_NAMES:
                        agg_t[-1] += 1
                    elif penl in OTHER_NAMES:
                        other_t[-1] += 1
                    elif penl not in exclude:
                        print('Penalty not found: {0:s}'.format(penl))
                    if penl not in total_pen_taken_dct:
                        total_pen_taken_dct[penl] = 0
                        total_pen_drawn_dct[penl] = 0
                    total_pen_taken_dct[penl] += 1
                    tsum += 1
            else:
                if player is None or player is [] or receiving_player(line) == player:
                    if penl in OBS_NAMES:
                        obs_d[-1] += 1
                    elif penl in DISC_NAMES:
                        disc_d[-1] += 1
                    elif penl in AGG_NAMES:
                        agg_d[-1] += 1
                    elif penl in OTHER_NAMES:
                        other_d[-1] += 1
                    elif penl not in exclude:
                        print('Penalty not found: {0:s}'.format(penl))
                    if penl not in total_pen_drawn_dct:
                        total_pen_drawn_dct[penl] = 0
                        total_pen_taken_dct[penl] = 0
                    total_pen_drawn_dct[penl] += 1
                    dsum += 1

    print('Total penalties')
    print('Name\tTaken\tDrawn')
    for penl in total_pen_taken_dct:
        print('{0:s}\t{1:d}\t{2:d}'.format(penl, total_pen_taken_dct[penl], total_pen_drawn_dct[penl]))
    print('Total taken: {0:d}\nTotal drawn: {1:d}'.format(tsum, dsum))

    obs_t_roll = []
    obs_d_roll = []
    agg_t_roll = []
    agg_d_roll = []
    disc_t_roll = []
    disc_d_roll = []
    other_t_roll = []
    other_d_roll = []

    for i in range(len(games)):
        start = max(0, i - roll_len)
        end = i
        obs_t_roll.append(sum(obs_t[start:end]))
        obs_d_roll.append(sum(obs_d[start:end]))
        agg_t_roll.append(sum(agg_t[start:end]))
        agg_d_roll.append(sum(agg_d[start:end]))
        disc_t_roll.append(sum(disc_t[start:end]))
        disc_d_roll.append(sum(disc_d[start:end]))
        other_t_roll.append(sum(other_t[start:end]))
        other_d_roll.append(sum(other_d[start:end]))

    import matplotlib.pyplot as plt

    # drawn
    if player is None or player == []:
        plt.title('{0:s} penalties drawn'.format(mascot_name(team)))
    else:
        plt.title('{0:s} {1:d} penalties drawn'.format(mascot_name(team), player))
    plt.xlabel(
        'End of team {2:d}-game rolling segment ({0:d}-{1:s})'.format(startseason, str(endseason + 1)[2:], roll_len))
    plt.grid(b=True, which='major', axis='y', linestyle='-')
    plt.grid(b=True, which='minor', axis='y', linestyle=':')
    obs_patch = plt.plot([], [], linewidth=4, color='c', label='Obstruction')
    disc_patch = plt.plot([], [], linewidth=4, color='g', label='Discipline')
    agg_patch = plt.plot([], [], linewidth=4, color='r', label='Aggression')
    other_patch = plt.plot([], [], linewidth=4, color='b', label='Other')
    plt.legend(loc=2, framealpha=0.5)
    plt.stackplot(games, obs_d_roll, disc_d_roll, agg_d_roll, other_d_roll, colors=('c', 'g', 'r', 'b'))
    plt.ylim(bottom=0)
    plt.xlim(0, len(games))
    plt.show()

    #taken
    plt.clf()
    if player is None or player == []:
        plt.title('{0:s} penalties taken'.format(mascot_name(team)))
    else:
        plt.title('{0:s} {1:d} penalties taken'.format(mascot_name(team), player))
    plt.xlabel(
        'End of team {2:d}-game rolling segment ({0:d}-{1:s})'.format(startseason, str(endseason + 1)[2:], roll_len))
    plt.grid(b=True, which='major', axis='y', linestyle='-')
    plt.grid(b=True, which='minor', axis='y', linestyle=':')
    obs_patch = plt.plot([], [], linewidth=4, color='c', label='Obstruction')
    disc_patch = plt.plot([], [], linewidth=4, color='g', label='Discipline')
    agg_patch = plt.plot([], [], linewidth=4, color='r', label='Aggression')
    other_patch = plt.plot([], [], linewidth=4, color='b', label='Other')
    plt.legend(loc=2, framealpha=0.5)
    plt.stackplot(games, obs_t_roll, disc_t_roll, agg_t_roll, other_t_roll, colors=('c', 'g', 'r', 'b'))
    plt.ylim(bottom=0)
    plt.xlim(0, len(games))
    plt.show()
    plt.clf()