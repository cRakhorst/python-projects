import csv
from collections import defaultdict
from datetime import datetime

def calculate_standings(csv_file_path):
    """
    Calculate league standings from match data
    """
    
    # Dictionary to store team stats: {team: {games, wins, draws, losses, goals_for, goals_against}}
    standings = defaultdict(lambda: {
        'games': 0,
        'wins': 0,
        'draws': 0,
        'losses': 0,
        'goals_for': 0,
        'goals_against': 0
    })
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            
            for row in csv_reader:
                home_team = row.get('HomeTeam', '').strip()
                away_team = row.get('AwayTeam', '').strip()
                
                try:
                    home_goals = int(row.get('FTHG', 0))
                    away_goals = int(row.get('FTAG', 0))
                    result = row.get('FTR', '').strip()
                    
                    # Update home team stats
                    standings[home_team]['games'] += 1
                    standings[home_team]['goals_for'] += home_goals
                    standings[home_team]['goals_against'] += away_goals
                    
                    # Update away team stats
                    standings[away_team]['games'] += 1
                    standings[away_team]['goals_for'] += away_goals
                    standings[away_team]['goals_against'] += home_goals
                    
                    # Update wins/draws/losses
                    if result == 'H':  # Home win
                        standings[home_team]['wins'] += 1
                        standings[away_team]['losses'] += 1
                    elif result == 'A':  # Away win
                        standings[away_team]['wins'] += 1
                        standings[home_team]['losses'] += 1
                    elif result == 'D':  # Draw
                        standings[home_team]['draws'] += 1
                        standings[away_team]['draws'] += 1
                
                except (ValueError, KeyError) as e:
                    continue
        
        # Calculate points and sort
        team_list = []
        for team, stats in standings.items():
            points = (stats['wins'] * 3) + (stats['draws'] * 1)
            goal_diff = stats['goals_for'] - stats['goals_against']
            
            team_list.append({
                'team': team,
                'games': stats['games'],
                'wins': stats['wins'],
                'draws': stats['draws'],
                'losses': stats['losses'],
                'goals_for': stats['goals_for'],
                'goals_against': stats['goals_against'],
                'goal_diff': goal_diff,
                'points': points
            })
        
        # Sort by points (desc), then by goal difference (desc), then by goals for (desc)
        team_list.sort(key=lambda x: (-x['points'], -x['goal_diff'], -x['goals_for']))
        
        return team_list
        
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found")
        return []

def write_sql_standings(standings_data, output_path):
    """Write standings to SQL file"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("-- ==================== LEAGUE STANDINGS ====================\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Create table
        f.write("""CREATE TABLE IF NOT EXISTS `standings` (
  `position` INT PRIMARY KEY,
  `team` VARCHAR(100) NOT NULL,
  `games` INT DEFAULT 0,
  `wins` INT DEFAULT 0,
  `draws` INT DEFAULT 0,
  `losses` INT DEFAULT 0,
  `goals_for` INT DEFAULT 0,
  `goals_against` INT DEFAULT 0,
  `goal_difference` INT DEFAULT 0,
  `points` INT DEFAULT 0
);

DELETE FROM `standings`;

-- ==================== INSERT DATA ====================
INSERT INTO `standings` (`position`, `team`, `games`, `wins`, `draws`, `losses`, `goals_for`, `goals_against`, `goal_difference`, `points`) VALUES
""")
        
        rows = []
        for position, team_data in enumerate(standings_data, 1):
            row = f"({position}, '{team_data['team'].replace(chr(39), chr(39)*2)}', {team_data['games']}, {team_data['wins']}, {team_data['draws']}, {team_data['losses']}, {team_data['goals_for']}, {team_data['goals_against']}, {team_data['goal_diff']}, {team_data['points']})"
            rows.append(row)
        
        f.write(",\n".join(rows))
        f.write(";\n")

def print_standings(standings_data):
    """Print standings in readable format"""
    
    print("\n" + "="*100)
    print(f"{'#':<3} {'Team':<25} {'G':<3} {'W':<3} {'Ge':<3} {'V':<3} {'GV':<3} {'GT':<3} {'DS':<5} {'Ptn':<4}")
    print("="*100)
    
    for position, team_data in enumerate(standings_data, 1):
        print(f"{position:<3} {team_data['team']:<25} {team_data['games']:<3} {team_data['wins']:<3} {team_data['draws']:<3} {team_data['losses']:<3} {team_data['goals_for']:<3} {team_data['goals_against']:<3} {team_data['goal_diff']:+<5} {team_data['points']:<4}")
    
    print("="*100 + "\n")

if __name__ == '__main__':
    csv_path = r'C:\Users\Chris\Downloads\N1.csv'
    sql_path = r'C:\Users\Chris\Documents\GitHub\python-shit\random-small-projects\test\standings.sql'
    
    standings = calculate_standings(csv_path)
    
    if standings:
        print_standings(standings)
        write_sql_standings(standings, sql_path)
        print(f"✓ SQL file created: {sql_path}")
    else:
        print("Error: Could not calculate standings")
