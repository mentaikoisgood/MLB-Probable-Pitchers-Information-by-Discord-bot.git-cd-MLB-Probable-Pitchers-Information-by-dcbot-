import requests
from datetime import datetime
import json
import mlbstatsapi

def get_pitcher_info(team):
    """獲取指定球隊的投手資訊"""
    try:
        # MLB Stats API
        url = f"https://statsapi.mlb.com/api/v1/teams"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # 獲取球隊ID
        response = requests.get(url, headers=headers)
        teams_data = response.json()
        team_id = None
        team_name = ""

        # 查找對應的球隊ID
        for team_info in teams_data['teams']:
            if team.upper() in team_info['abbreviation'] or team.upper() in team_info['teamName'].upper():
                team_id = team_info['id']
                team_name = team_info['name']
                break

        if not team_id:
            return f"找不到球隊 {team}"

        # 獲取該球隊的比賽資訊
        schedule_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/probablepitchers"
        schedule_response = requests.get(schedule_url, headers=headers)
        pitcher_data = schedule_response.json()

        if not pitcher_data:
            return f"暫時沒有 {team_name} 的投手資訊"

        # 格式化輸出
        output = f"**{team_name} 投手資訊**\n"
        output += "預計先發投手資訊將在比賽日更新"

        return output

    except Exception as e:
        return f"獲取資料時發生錯誤: {str(e)}\n請稍後再試"


def get_schedule():
    """獲取今日比賽賽程"""
    try:
        # MLB Stats API
        today = datetime.now().strftime("%Y-%m-%d")
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers)
        schedule_data = response.json()

        if not schedule_data.get('dates'):
            return "今天沒有比賽安排"

        games = schedule_data['dates'][0]['games']
        output = f"**{today} 比賽賽程**\n"

        for game in games:
            away_team = game['teams']['away']['team']['name']
            home_team = game['teams']['home']['team']['name']
            game_time = datetime.strptime(
                game['gameDate'], "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M")
            output += f"{away_team} @ {home_team} - {game_time}\n"

        return output

    except Exception as e:
        return f"獲取賽程時發生錯誤: {str(e)}\n請稍後再試"


def get_all_teams():
    """獲取所有MLB球隊列表"""
    try:
        url = "https://statsapi.mlb.com/api/v1/teams?sportId=1"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers)
        teams_data = response.json()

        output = "**MLB球隊列表**\n"
        for team in teams_data['teams']:
            output += f"{team['name']} ({team['abbreviation']})\n"

        return output

    except Exception as e:
        return f"獲取球隊列表時發生錯誤: {str(e)}"


def get_game_history(team, date=None):
    """獲取指定日期的比賽歷史"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}&teamId="
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # 先獲取球隊ID
        teams_response = requests.get(
            "https://statsapi.mlb.com/api/v1/teams", headers=headers)
        teams_data = teams_response.json()
        team_id = None

        for team_info in teams_data['teams']:
            if team.upper() in team_info['abbreviation'] or team.upper() in team_info['teamName'].upper():
                team_id = team_info['id']
                break

        if not team_id:
            return f"找不到球隊：{team}"

        # 獲取比賽歷史
        history_url = url + str(team_id)
        history_response = requests.get(history_url, headers=headers)
        history_data = history_response.json()

        output = f"**{team} 在 {date} 的比賽記錄**\n"
        if not history_data.get('dates'):
            return f"{date} 沒有比賽記錄"

        for game in history_data['dates'][0]['games']:
            away_team = game['teams']['away']['team']['name']
            home_team = game['teams']['home']['team']['name']
            away_score = game['teams']['away'].get('score', 'N/A')
            home_score = game['teams']['home'].get('score', 'N/A')
            output += f"{away_team} {away_score} @ {home_team} {home_score}\n"

        return output

    except Exception as e:
        return f"獲取歷史資料時發生錯誤: {str(e)}"


def get_recent_games(team, games=3):
    """獲取球隊最近的比賽數據"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # 先獲取球隊ID
        teams_response = requests.get(
            "https://statsapi.mlb.com/api/v1/teams", headers=headers)
        teams_data = teams_response.json()
        team_id = None
        team_name = ""

        for team_info in teams_data['teams']:
            if team.upper() in team_info['abbreviation'] or team.upper() in team_info['teamName'].upper():
                team_id = team_info['id']
                team_name = team_info['name']
                break

        if not team_id:
            return f"找不到球隊：{team}"

        # 獲取最近比賽記錄
        # 我們多請求一些數據以確保能獲取到足夠的已完成比賽
        schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?teamId={team_id}&sportId=1&gameType=R&season=2024&startDate=2024-01-01&endDate=2024-12-31"
        schedule_response = requests.get(schedule_url, headers=headers)
        schedule_data = schedule_response.json()

        if not schedule_data.get('dates'):
            return f"找不到 {team_name} 的比賽記錄"

        # 收集所有比賽
        completed_games = []
        for date in schedule_data['dates']:
            for game in date['games']:
                if game['status']['statusCode'] == 'F':  # 只獲取已完成的比賽
                    completed_games.append(game)

        # 取最近的幾場比賽
        recent_games = completed_games[-int(games):]

        output = f"**{team_name} 最近 {len(recent_games)} 場比賽記錄**\n"
        for game in recent_games:
            game_date = datetime.strptime(
                game['gameDate'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            away_team = game['teams']['away']['team']['name']
            home_team = game['teams']['home']['team']['name']
            away_score = game['teams']['away']['score']
            home_score = game['teams']['home']['score']

            # 判斷該隊是主場還是客場，並標記勝負
            if team_id == game['teams']['away']['team']['id']:
                result = "勝" if away_score > home_score else "敗"
            else:
                result = "勝" if home_score > away_score else "敗"

            output += f"{game_date}: {away_team} {away_score} @ {home_team} {home_score} [{result}]\n"

        return output

    except Exception as e:
        return f"獲取最近比賽資料時發生錯誤: {str(e)}"

def get_hitter_stat(player):
    selected = ["gamesplayed", "groundouts", "airouts", "runs", "doubles", "triples", "homeruns", "strikeouts", "baseonballs", "intentionalwalks", "hits", "hitbypitch", "avg", "atbats", "obp", "slg", "ops", "caughtstealing", "stolenbases", "stolenbasepercentage", "plateappearances", "sacbunts", "sacflies", "babip", "groundoutstoairouts", "atbatsperhomerun"]
    mlb = mlbstatsapi.Mlb()
    player_id = mlb.get_people_id(player)[0]
    stats = ['season', 'seasonAdvanced']
    groups = ['hitting']
    params = {'season': 2024}
    mlb.get_player_stats(player_id, stats, groups, **params)
    stat_dict = mlb.get_player_stats(player_id, stats=stats, groups=groups, **params)
    season_hitting_stat = stat_dict['hitting']['season']
    string = ""
    for split in season_hitting_stat.splits:
        for k, v in split.stat.__dict__.items():
            if k in selected:
                string += str(k) + ": " + str(v) + "\n"
    return string

def get_pitcher_stat(player):
    selected = ["gamesplayed", "gamesstarted", "groundouts", "airouts", "runs", "doubles", "triples", "homeruns", "strikeouts", "baseonballs", "hits", "hitbypitch", "avg", "atbats", "obp", "slg", "ops", "caughtstealing", "stolenbases", "stolenbasepercentage", "numberofpitches", "inningspitched", "whip", "strikepercentage", "wildpitches", "pickoffs", "groundoutstoairouts", "pitchesperinning", "strikeoutwalkratio", "strikeoutsper9inn", "walksper9inn", "hitsper9inn", "runsscoredper9", "homerunsper9", "sacbunts", "sacflies", "battersfaced"]
    mlb = mlbstatsapi.Mlb()
    player_id = mlb.get_people_id(player)[0]
    stats = ['season', 'seasonAdvanced']
    groups = ['pitching']
    params = {'season': 2024}
    mlb.get_player_stats(player_id, stats, groups, **params)
    stat_dict = mlb.get_player_stats(player_id, stats=stats, groups=groups, **params)
    season_pitching_stat = stat_dict['pitching']['season']
    string = ""
    for split in season_pitching_stat.splits:
        for k, v in split.stat.__dict__.items():
            if k in selected:
                string += str(k) + ": " + str(v) + "\n"
    return string