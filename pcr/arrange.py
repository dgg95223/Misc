import numpy as np

def get_name(players_num:int, type=None):
    assert type is not None, 'Warn: please specify the type of name.'
    assert type is 'full' or 'player' or 'team' or 'boss', 'The type of name specified is not supported.'

    name = []
    for i in range(0, players_num):
        if type == 'player':
            name.append(str(i+1))
        for j in range(0, 3):
            for k in range(0, 5):
                if type == 'full':
                    name.append(str(i+1)+'-'+str(j+1)+'-'+str(k+1))

    if type == 'team':
        for i in range(0, 3):
            name.append(str(i+1))
    if type == 'boss':
        for i in range(0, 5):
            name.append(str(i+1))
    return name

def get_damages(path:str):
    damages = np.loadtxt(path)
    damages_0 = damages.flatten()
    return damages_0

def get_box(players_num:int, damages:list):
    full_name = get_name(players_num, type='full')
    # print(len(full_name))
    box = {} # Dict
    for i in range(0, len(full_name)):
        box.update({full_name[i]:damages[i]})
    return box

def get_name_player(player:str, name:list):
    player_0 = player + '-'
    if int(player) >= 10:
        name_0 = [i for i in name if player_0 in i[0:3]]
    else:
        name_0 = [i for i in name if player_0 in i[0:2]]
    return name_0

def get_name_boss(boss:str, name:list):
    boss_0 = '-' + boss
    name_0 = [i for i in name if boss_0 in i[3:]]
    return name_0

def get_name_team(team:str, name:list):
    team_0 = '-' + team + '-'
    name_0 = [i for i in name if team_0 in i[-4:-1]]
    return name_0

def cal_weight_boss(player:str, team:str, boss:str, name:list, box:dict):
    name_player = get_name_player(player, name)
    name_player_team = get_name_team(team, name_player)
    # print(name_player_team)

    weights = np.zeros(len(name_player_team))
    alter_name = []
    alter_dam = []

    for i in range(0, len(name_player_team)):
        # weights[i] = box[name_player_team[i]] / box[name_player_team[int(boss) - 1]]
        weights[i] = box[name_player_team[int(boss) - 1]] - box[name_player_team[i]]
        # print(box[name_player_team[i]])

        if weights[i] >= 1:
            alter_name.append(name_player_team[i])
            alter_dam.append(box[name_player_team[i]])
            # print('attention! %s'%name_player_team[i])
    
    name_sorted_weights = [i for _, i in sorted(zip(weights, name_player_team), reverse=True)]
    weights_sorted = [i for i in sorted(weights, reverse=True)]
    return weights_sorted, name_sorted_weights

# print(cal_weight_boss('1', '2', '2', name, box))

def get_index_bosses_cycle(dict_bosses:dict, cycle:int, boss_current:str):
    if boss_current =='K1':
        tag = 0
    elif boss_current == 'K2':
        tag = 1
    elif boss_current == 'K3':
        tag = 2
    elif boss_current == 'K4':
        tag = 3
    elif boss_current == 'K5':
        tag = 4
    else:
        print("Please enter the name of boss as 'Kx', where x is 1, 2, 3, 4, 5")
        error = 1
        assert error == 0, 'Arrangement abortted'
    
    list = []

    index = tag
    iboss = 0
    bosses = [*dict_bosses]

    while iboss < len(bosses) * cycle:
        list.append(bosses[index])
        iboss += 1
        index += 1
        if index > 4:
            index = 0
    return list

# print(get_index_bosses_cycle(boss, 2, 'K2'))

def arrange(players_num:int, bosses:dict, box:dict, boss_current:str, dam_current=None, cycle=None, **options):
    ### Initialization ###
    if dam_current == None:
        dam_current = 0

    if dam_current is not 0:
        bosses[boss_current] = dam_current

    if cycle == None:
        cycle = 1
        # For cycle which is more than 1 is not available at this point. --6/25/2020

    boss_list = get_index_bosses_cycle(bosses, cycle, boss_current)
    name = get_name(players_num, type='full')
    players = get_name(players_num, type='player')
    teams = get_name(players_num, type='team')

    weights = []
    keys = []
    arrange = []
    damages = []
    _box = box
    
    boss_arrange = []
    keys_remove = []

    for iboss, boss in enumerate(boss_list):
        
        print('Current boss: %s'%boss)
        _temp_name_boss = get_name_boss(boss[-1], name)
        boss_arrange.append(_temp_name_boss)
        # print(boss_arrange)

        weights_list = []
        keys_list = []
        
        for iplayer, player in enumerate(players):
            for iteam , team in enumerate(teams):
                _temp_weights, _temp_keys = cal_weight_boss(player, team, boss[-1], name, box)
                weights_list.append(_temp_weights)
                keys_list.append(_temp_keys)
        
        weights.append(weights_list)
        keys.append(keys_list)
        weights_dict = {boss_arrange[iboss][i]:(weights[iboss][i], keys[iboss][i]) for i in range(0,len(boss_arrange[iboss]))}

        ### Sorting starts here ###
        dam_boss = {k: box[k] for k in _temp_name_boss}
        dam_boss_sorted = {k: v for k, v in sorted(dam_boss.items(), key=lambda item: item[1], reverse=True)}
        keys_sorted = [*dam_boss_sorted]
        
        if keys_remove == []:
            pass
        else:
            for key in keys_remove:
                keys_sorted.remove(key[:-1]+boss[-1])
                
        dam_sorted_list = [dam_boss_sorted[i] for i in keys_sorted]
        # print('dict:',weights_dict)

        damage = 0
        index = 0
        arranged = []

        # damage_preserve = 40
        while damage < bosses[boss]:
            if weights_dict[keys_sorted[index]][0][0] >= -5:
                damage += dam_sorted_list[index]
                arranged.append(keys_sorted[index])
            index += 1

        rest = keys_sorted[index:]
        rest_dam_list = [box[i] for i in rest]
        rest_dam = sum(rest_dam_list)
        
        arrange.append(arranged)
        damages.append(damage)
        keys_remove += arranged

        for i in arranged:
            print('%4s: %3d'%(i[:-2],box[i]))
        print('Total damage: %d/%d'%(damage,bosses[boss]))
        print('Number of rest team:', len(rest))
        if rest_dam < bosses[boss_list[iboss+1]]:
            print('\nThe rest of damage, %d, is not enough to defeat the next boss.'%rest_dam)
            print('The rest of teams are:',*[i[:-2] for i in rest])
            break
        print('')

    return arrange


damages = get_damages('test.txt')
boss = {'K1':100, 'K2':100, 'K3':50, 'K4':800, 'K5':500} # Dict
box =  get_box(10, damages)
a = arrange(10, boss, box, 'K2', dam_current=80)
