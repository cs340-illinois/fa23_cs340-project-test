kill -9 `cat pids.txt`
> pids.txt

VOTES=8 IMAGE=red.png TILE=red-tile.png flask run --port=5001 &
echo $! >> pids.txt

VOTES=9 IMAGE=blue.png TILE=blue-tile.png flask run --port=5002 &
echo $! >> pids.txt

VOTES=7 IMAGE=green.png TILE=green-tile.png flask run --port=5003 &
echo $! >> pids.txt
