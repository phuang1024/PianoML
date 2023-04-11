# Piano ML

Hackathon project by
[PeaceOfPi](https://github.com/PeaceOfPi),
[Sinha-Soumik](https://github.com/Sinha-Soumik),
[The-Senate-I-Am](https://github.com/The-Senate-I-Am),
and [phuang1024](https://github.com/phuang1024)

## Running Locally

```bash
pip install -r requirements.txt
```

### ML Server

The ML autocomplete program is run as a server separate from the GUI. (They could be run
from the same computer.)

You also need to obtain a model. I have trained a model, which you can download at this link

https://drive.google.com/file/d/1zXGMuueuYocWr0hC9wyOJsqzEnHa8h3k/view?usp=share_link

```bash
cd ml

# Save model to this file:
mkdir results
mv /path/to/model.pt results/model.pt

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
