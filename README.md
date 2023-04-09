# Piano ML

## Running Locally

```bash
pip install -r requirements.txt
```

### ML Server

The ML autocomplete program is run as a server separate from the GUI. (They could be run
from the same computer.)

```bash
cd ml
python server.py
```

### GUI

```bash
cd gui
python main.py --ip ip_of_server
```

## GUI Usage

The GUI is a basic MIDI recording system with a fixed length of 30 seconds.
Playing the piano is done via keyboard; use the keys `awsedftgyhujkolp;'`, which resemble
the keys on a piano. Use the keys `z` and `x` to move down and up octaves.

Press the `Record` button and play a melody. Press the `Stop` button to end recording.

Press the `Autocomplete` button to query the ML program. The neural network will return
a completion after the last note you have recorded.
