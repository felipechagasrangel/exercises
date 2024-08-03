# This solves GiantSteps 15 Exercise


## Introduction

This code runs many configurations of coins and finds the ones that minimizes the mean of coins in the representation of 1 to 100 (both included)

To avoid RAM consumption, I dont have many, I use generators and parallelize using ProcessPoolExecutor.

I only save one of the best results. Could be more than one, is a minor adjustment but I'm lazy.

obs: If you remove 100 from your mean the answer could change.

## How to

To run this code you should create a virtual environment.

python -m venv venv

Then run src/main.py


