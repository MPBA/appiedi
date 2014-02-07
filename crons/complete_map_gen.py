from main import gen_map, move_to_db
import time

def main():
    t = time.time()
    for dow in range(7):
        print 'generating DOW map for dow n. {0}'.format(dow)
        gen_map(0.0, t, 'dow_{0}'.format(dow), dow)
        print '...and moving it to DB'
        move_to_db('dow_{0}'.format(dow), 'co_dow{0}'.format(dow))

if __name__ == '__main__':
    main()
