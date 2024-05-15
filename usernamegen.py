import requests
from requests.auth import HTTPBasicAuth
import random
import string
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from dkimgen import generate_dkim_key


def generate_friendly_username():
    words = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"]
    username = random.choice(words) + random.choice(words) + str(random.randint(10, 99))
    return username