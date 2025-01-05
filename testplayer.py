import mlbstatsapi
mlb = mlbstatsapi.Mlb()
player_id = mlb.get_people_id("Luis Gil")[0]
stats = ['season', 'seasonAdvanced']
groups = ['pitching']
params = {'season': 2024}
mlb.get_player_stats(664034, stats, groups, **params)
stat_dict = mlb.get_player_stats(player_id, stats=stats, groups=groups, **params)
season_hitting_stat = stat_dict['pitching']['season']
#career_pitching_stat = stat_dict['pitching']['career']

for split in season_hitting_stat.splits:
    for k, v in split.stat.__dict__.items():
        print(k, v)