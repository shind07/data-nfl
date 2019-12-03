import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Game(Base):
    __tablename__ = 'games'

    type = sa.Column(sa.VARCHAR(length=16), autoincrement=False, nullable=False)
    game_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=False, primary_key=True)
    home_team = sa.Column(sa.VARCHAR(length=16), autoincrement=False, nullable=False)
    away_team = sa.Column(sa.VARCHAR(length=16), autoincrement=False, nullable=False)
    week = sa.Column(sa.SMALLINT(), autoincrement=False, nullable=False)
    season = sa.Column(sa.SMALLINT(), autoincrement=False, nullable=False)
    state_of_game = sa.Column(sa.VARCHAR(length=16), autoincrement=False, nullable=False)
    game_url = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=False)
    home_score = sa.Column(sa.SMALLINT(), autoincrement=False, nullable=True)
    away_score = sa.Column(sa.SMALLINT(), autoincrement=False, nullable=True)

    def __repr__(self):
        return f"<Game((H) {self.home_team} {self.home_score} - {self.away_score} {self.away_team} (A))>"
