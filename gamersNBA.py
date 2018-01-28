from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbase_setup import Franchise, Base, Player, User

engine = create_engine('sqlite:///gamersnba.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# users created
simon = User(name="Simon Templar", email="simonTemplar@udacity.com",
             picture='https://pbs.twimgdaSD.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(simon)
session.commit()

jude = User(name="Jude Kuti", email="judekuti@udacity.com",
            picture='https://pbs.twimdgdaSD.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(jude)
session.commit()

# Cleveland Cavaliers
cavs = Franchise(name="Cleveland Cavaliers", user_id=1, image="allstar.jpg")

session.add(cavs)
session.commit()

lebron = Player(name='Lebron James',
                age=32,
                price='$3 million',
                height='6 feet 8 inches',
                weight='280 pounds',
                ppg=27,
                position='Small Forward',
                image='nbastars.jpg',
                youtube_url='https://www.youtube.com/watch?v=GJ9OQLovpr4',
                franchise=cavs,
                user_id=1)
session.add(lebron)
session.commit()

TT = Player(name='Tristan Thompson',
                 age=28,
                 price='$1.2 million',
                 height='6 feet 10 inches',
                 weight='290 pounds',
                 ppg=10,
                 position='Center',
                 image='nbastars.jpg',
                 youtube_url='https://www.youtube.com/watch?v=GJ9OQLovpr4',
                 franchise=cavs,
                 user_id=1)
session.add(TT)
session.commit()

JR = Player(name='JR Smith',
                 age=33,
                 price='$1 million',
                 height='6 feet 5 inches',
                 weight='240 pounds',
                 ppg=15,
                 position='Point Guard',
                 image='nbastars.jpg',
                 youtube_url='https://www.youtube.com/watch?v=GJ9OQLovpr4',
                 franchise=cavs,
                 user_id=1)
session.add(JR)
session.commit()

IT = Player(name='Isaiah Thomas',
                 age=28,
                 price='$1.5 million',
                 height='5 feet 9 inches',
                 weight='180 pounds',
                 ppg=26,
                 position='Shooting Guard',
                 image='nbastars.jpg',
                 youtube_url='https://www.youtube.com/watch?v=GJ9OQLovpr4',
                 franchise=cavs,
                 user_id=1)
session.add(IT)
session.commit()

jay = Player(name='Jay Crowther',
             age=24,
             price='$1.1 million',
             height='6 feet 6 inches',
             weight='230 pounds',
             ppg=15,
             position='Power Forward',
             image='nbastars.jpg',
             youtube_url='https://www.youtube.com/watch?v=GJ9OQLovpr4',
             franchise=cavs,
             user_id=1)
session.add(jay)
session.commit()


# Golden State Warriors
gsw = Franchise(name="Golden State Warriors", user_id=2, image="cort2.jpg")
session.add(gsw)
session.commit()

steph = Player(name='Steph Curry',
               age=27,
               price='$3 million',
               height='6 feet 5 inches',
               weight='200 pounds',
               ppg=29,
               position='Shooting Guard',
               image='nbastars.jpg',
               youtube_url='https://www.youtube.com/watch?v=GJ9OQLovpr4',
               franchise=gsw,
               user_id=2)
session.add(steph)
session.commit()

KD = Player(name='Kevin Durant',
                 age=29,
                 price='$3 million',
                 height='6 feet 10 inches',
                 weight='275pounds',
                 ppg=28,
                 position='Power Forward',
                 image='nbastars.jpg',
                 youtube_url='https://www.youtube.com/watch?v=GJ9OQLovpr4',
                 franchise=gsw,
                 user_id=2)
session.add(KD)
session.commit()

klay = Player(name='Klay Thompson',
              age=28,
              price='$2.5 million',
              height='6 feet 7 inches',
              weight='235pounds',
              ppg=22,
              position='Point Guard',
              image='nbastars.jpg',
              youtube_url='https://www.youtube.com/watch?v=GJ9OQLovpr4',
              franchise=gsw,
              user_id=2)
session.add(klay)
session.commit()

dramond = Player(name='Dramond Green',
                 age=29,
                 price='$1 million',
                 height='6 feet 10 inches',
                 weight='285pounds',
                 ppg=13,
                 position='Small Forward',
                 image='nbastars.jpg',
                 youtube_url='https://www.youtube.com/watch?v=GJ9OQLovpr4',
                 franchise=gsw,
                 user_id=2)
session.add(dramond)
session.commit()

zaza = Player(name='Zaza Pachulia',
              age=34,
              price='$1 million',
              height='7 feet 0 inches',
              weight='290 pounds',
              ppg=6,
              position='Center',
              image='nbastars.jpg',
              youtube_url='https://www.youtube.com/watch?v=GJ9OQLovpr4',
              franchise=gsw,
              user_id=2)
session.add(zaza)
session.commit()
