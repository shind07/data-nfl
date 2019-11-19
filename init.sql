CREATE TABLE IF NOT EXISTS games 
  ( 
     `type`          VARCHAR(16) NOT NULL, 
     `game_id`       INTEGER PRIMARY KEY, 
     `home_team`     VARCHAR(16) NOT NULL, 
     `away_team`     VARCHAR(16) NOT NULL, 
     `week`          SMALLINT NOT NULL, 
     `season`        SMALLINT NOT NULL, 
     `state_of_game` VARCHAR(16) NOT NULL, 
     `game_url`      VARCHAR(255) NOT NULL, 
     `home_score`    SMALLINT, 
     `away_score`    SMALLINT 
  );


"""
type,game_id,home_team,away_team,week,season,state_of_game,game_url,home_score,away_score

https://rdrr.io/github/maksimhorowitz/nflscrapR/man/game_play_by_play.html
"""