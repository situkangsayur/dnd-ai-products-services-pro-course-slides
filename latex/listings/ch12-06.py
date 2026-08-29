[(k, v.shape) for k, v in predictions.items()]
# [("boxes", (1, 100, 4)),
#  ("confidence", (1, 100)),
#  ("labels", (1, 100)),
#  ("num_detections", (1,))]

predictions["boxes"][0][0]
