import jax
from jax import numpy as jnp

jnp.ones(shape=(2, 1))              # API NumPy, tanpa penyimpangan

# Tidak ada keadaan acak global: kunci diberikan secara eksplisit
seed_key = jax.random.key(123)
jax.random.normal(seed_key, shape=(3,))     # kunci sama -> nilai sama, selalu
key1, key2 = jax.random.split(seed_key)     # cara membuat kunci baru

# Array kekal: perbarui dengan menghasilkan array baru
x = jnp.array([1, 2, 3], dtype="float32")
new_x = x.at[0].set(10)
