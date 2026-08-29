prompt1 = "A friendly dog looking up in a field of flowers"
prompt2 = ("A horrifying, tentacled creature hovering over a field of "
           "flowers")

e1 = get_text_embeddings(prompt1)
e2 = get_text_embeddings(prompt2)

images = []
for et in interpolate_text_embeddings(e1, e2, start=0.5, stop=0.6, num=9):
    image = denoise_with_text_embeddings(et)
    images.append(scale_output(image))
display(images)
