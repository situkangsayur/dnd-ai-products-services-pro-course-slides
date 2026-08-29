import jax
from jax import numpy as jnp

jnp.ones(shape=(2, 1))              # the NumPy API, with no divergence

seed_key = jax.random.key(123)
jax.random.normal(seed_key, shape=(3,))     # same key -> same value, always
key1, key2 = jax.random.split(seed_key)     # how you get a fresh key

x = jnp.array([1, 2, 3], dtype="float32")
new_x = x.at[0].set(10)             # arrays are immutable: you get a new one
