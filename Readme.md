# Deep Q learning on Helicopter
This project presents an effective way to play the popular Helicopter game using a convolutional neural network 
to estimate the Q-function, using visual input of the game. It uses techniques described in [1] and improves
upon it to play this specific game. 

# Dependencies
* Python 2.7
* Pygame
* Tensorflow
* OpenCV-Python

# Running
```
git clone https://github.com/nishanthpp93/heli-dqn.git
python deep_q_n.py
```

# References
[1] Mnih Volodymyr, Koray Kavukcuoglu, David Silver, Andrei A. Rusu, Joel Veness, Marc G. Bellemare, Alex Graves, 
Martin Riedmiller, Andreas K. Fidjeland, Georg Ostrovski, Stig Petersen, Charles Beattie, Amir Sadik, Ioannis 
Antonoglou, Helen King, Dharshan Kumaran, Daan Wierstra, Shane Legg, and Demis Hassabis. Human-level Control 
through Deep Reinforcement Learning. Nature, 529-33, 2015.

[2] Volodymyr Mnih, Koray Kavukcuoglu, David Silver, Alex Graves, Ioannis Antonoglou, Daan Wierstra, and Martin 
Riedmiller. Playing Atari with Deep Reinforcement Learning. NIPS, Deep Learning workshop

# Disclaimer

This work is highly based on the following repos:

* [asrivat1/DeepLearningVideoGames](https://github.com/asrivat1/DeepLearningVideoGames)
* [yenchenlin/DeepLearningFlappyBird](https://github.com/yenchenlin/DeepLearningFlappyBird)
