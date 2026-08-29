gemma_lm.preprocessor.max_images_per_prompt = 1
gemma_lm.preprocessor.sequence_length = 512

prompt = "What is going on in this image? Be concise!<start_of_image>"
gemma_lm.generate({
    "prompts": PROMPT_TEMPLATE.format(prompt),
    "images": [image],
})
