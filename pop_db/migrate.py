from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer,Text, MetaData, ForeignKey,TIMESTAMP

engine = create_engine("postgresql://postgres:aaaa@localhost/easybuy", echo=True)


metadata = MetaData()

queries_table = Table('queries', metadata,
    Column('user', Text),
    Column('time', TIMESTAMP),
    Column('sex', Text),
    Column('cat', Text),

)

sent_table = Table('sent', metadata,
    Column('user', Text),
    Column('good_id', Text),
    Column('time', TIMESTAMP)
)



metadata.create_all(engine)