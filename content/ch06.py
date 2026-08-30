# -*- coding: utf-8 -*-
"""Chapter 6 — The universal workflow of machine learning.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 6
(pp. 171-189), read from the book PDF.

The chapter closest to a practitioner's daily work: framing, data collection,
ethics, shipping, monitoring, and concept drift. The fraud-threshold example in
6.3.1 is the book's own, with the book's numbers -- not any organisation's.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_WORKFLOW = """
flowchart LR
  A["<b>1 · Define the task</b><br/>frame the problem<br/>collect and annotate data<br/>choose a success measure"]
  B["<b>2 · Develop a model</b><br/>prepare the data<br/>beat a baseline<br/>scale up, then regularise"]
  C["<b>3 · Deploy</b><br/>set expectations<br/>ship inference<br/>monitor and maintain"]
  A --> B --> C
  C -. "new production data<br/>feeds the next generation" .-> A
"""

MMD_DRIFT = """
flowchart LR
  F["Credit-card fraud<br/><b>days</b>"] --> M["Music recommender<br/><b>weeks</b>"]
  M --> I["Image search engine<br/><b>a couple of years, at best</b>"]
"""

MMD_DEPLOY = """
flowchart TB
  Q1{"Is the input data<br/>highly sensitive, or<br/>connectivity poor?"}
  Q2{"Strict latency<br/>requirements?"}
  Q3{"Do you want to move<br/>compute to the user?"}
  API["REST API<br/><small>~500 ms round trip</small>"]
  DEV["On device<br/><small>TF Lite, ONNX runtime</small>"]
  BR["In the browser<br/><small>TensorFlow.js, ONNX JS</small>"]
  Q1 -- yes --> DEV
  Q1 -- no --> Q2
  Q2 -- yes --> Q3
  Q2 -- no --> API
  Q3 -- yes --> BR
  Q3 -- no --> API
"""

MMD_LEAKCHECK = """
flowchart TB
  F["A feature in your training data"]
  Q{"Will it exist, in the<br/>same form, at the moment<br/>the model must decide?"}
  OK["Safe to use"]
  BAD["<b>Target leak</b><br/>remove it"]
  F --> Q
  Q -- yes --> OK
  Q -- no --> BAD
"""

MMD_OPTIMISE = """
flowchart LR
  M["Trained model<br/>float32"]
  P["Weight pruning<br/><small>keep only the<br/>significant coefficients</small>"]
  Q["Weight quantization<br/><small>float32 to int8</small>"]
  S["4x smaller,<br/>near the original accuracy"]
  M --> P --> Q --> S
"""


MMD_STAGES = """
flowchart LR
  S1["<b>Stage 1</b><br/>Beat a baseline<br/><small>statistical power</small>"]
  S2["<b>Stage 2</b><br/>Scale up<br/><small>until it overfits</small>"]
  S3["<b>Stage 3</b><br/>Regularise and tune<br/><small>maximise generalisation</small>"]
  S1 --> S2 --> S3
  S3 -. "if test << validation,<br/>your protocol was not reliable" .-> S3
"""

NB = ["01_understand_data_before_modelling.ipynb", "02_common_preprocessing.ipynb",
      "03_export_and_quantize.ipynb"]

DECK = {
    "id": "ch06",
    "kind": "chapter",
    "number": 6,
    "title": "The Universal Workflow of Machine Learning",
    "subtitle": "You do not start from a dataset. You start from a problem — and "
                "the hardest work happens before the first line of model code.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 6",
    "source_url": chapter_url(6),
    "duration": "3 hours (2 sessions)",
    "presenter": [
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
    ],
    "resources": chapter_resources(6, local_notebooks=NB),
    "objectives": [
        "Frame a business problem as the right **kind of machine learning task** — "
        "including recognising when machine learning is **not** the answer.",
        "Name the **two hypotheses** you make silently at the start of every "
        "project, and what it means if either is false.",
        "Design collection and annotation so the data **represents production**, "
        "and recognise **sampling bias**, **target leaks**, and **concept drift**.",
        "Choose a success measure, then choose the **last-layer activation, loss, "
        "and metrics** that match it.",
        "Run the three development stages: **beat a baseline → scale up until it "
        "overfits → regularise and tune**.",
        "Choose a deployment route — **REST API, on device, or in the browser** — "
        "and optimise the model for inference.",
        "Set stakeholder expectations in **false-positive and false-negative** "
        "terms rather than \"98% accurate\".",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Opening",
            "title": "In the real world, `keras.datasets` does not exist",
            "blocks": [
                {"t": "lead", "md": "Imagine opening your own machine learning consultancy. "
                                    "The projects start rolling in — and ==not one of them "
                                    "arrives with its dataset=="},
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "🔍", "h": "Photo search",
                     "p": "Type *wedding*, get every wedding photo — with no manual tagging."},
                    {"ico": "🚫", "h": "Spam and abuse",
                     "p": "Flagging posts in a growing chat app."},
                    {"ico": "🎵", "h": "Music recommendation",
                     "p": "For the users of an online radio station."},
                    {"ico": "💳", "h": "Credit-card fraud",
                     "p": "For an e-commerce site."},
                    {"ico": "📢", "h": "Ad click-through rate",
                     "p": "Deciding which ad to serve to whom, and when."},
                    {"ico": "🍪", "h": "Defective biscuits",
                     "p": "Flagging anomalies on a factory conveyor belt."},
                    {"ico": "🛰", "h": "Archaeological sites",
                     "p": "Locating undiscovered ones from satellite imagery."},
                    {"ico": "🏢", "h": "…and your own case",
                     "p": "Which you will carry through this chapter as the group assignment.",
                     "style": "accent"},
                ]},
            ],
            "notes": "Have each participant pick one case from their own work at the start "
                     "and carry it through every stage. That becomes the assignment.",
        },

        {
            "type": "slide",
            "kicker": "Roadmap",
            "title": "Three parts — and the hard one comes first",
            "blocks": [
                {"t": "mmd", "id": "ch06-workflow", "src": MMD_WORKFLOW,
                 "cap": "Note the return arrow: the loop never actually closes."},
                {"t": "quote",
                 "md": "Model development is only one step in the machine learning workflow, "
                       "and if you ask us, it's not the most difficult one. The hardest things "
                       "in machine learning are framing problems and collecting, annotating, "
                       "and cleaning data.",
                 "cite": "Chollet & Watson, section 6.2"},
            ],
        },

        {"type": "section", "num": "01", "title": "Defining the task",
         "lead": "You cannot do good work without deeply understanding the context."},

        {
            "type": "slide",
            "kicker": "Section 6.1.1",
            "title": "Four questions to keep at the front of your mind",
            "blocks": [
                {"t": "steps", "items": [
                    "**What will the input data be? What are you trying to predict?** You can "
                    "only learn to predict something you have training data for. "
                    "==Data availability is usually the limiting factor here.==",
                    "**What type of task is this?** Binary? Multiclass? Scalar regression? "
                    "Segmentation? Ranking? Or — quite possibly — **machine learning is not "
                    "the best way** and plain statistics would serve better.",
                    "**What do existing solutions look like?** Perhaps a hand-crafted "
                    "algorithm full of nested `if` statements. Perhaps a person doing it "
                    "manually today. Understand what is already in place.",
                    "**Are there particular constraints?** End-to-end encryption may force "
                    "the model onto the user's phone. Latency may force it onto an embedded "
                    "device at the factory rather than a remote server.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.1",
            "title": "Why the third question matters more than it looks",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "In most real projects the baseline is **not** \"random\". It is a "
                       "rules-based system that has been running for years and that people "
                       "already trust — and ==that is a much harder thing to beat=="},
                {"t": "p", "md": "It is also the thing you will be compared against when the "
                                 "project is reviewed, so it should be measured properly at "
                                 "the start rather than described from memory."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.1",
            "title": "The seven examples, mapped to task types",
            "blocks": [
                {"t": "table",
                 "head": ["Project", "Task type", "Note"],
                 "widths": [22, 28, 50],
                 "rows": [
                     ["Photo search", "**Multiclass, multilabel**", "—"],
                     ["Spam", "**Binary**",
                      "Becomes **three-way** if *offensive content* is a separate class."],
                     ["Music recommendation", "==Not deep learning==",
                      "Better handled by **matrix factorisation** (collaborative filtering)."],
                     ["Credit-card fraud", "**Binary**", "—"],
                     ["Click-through rate", "**Scalar regression**", "—"],
                     ["Defective biscuits", "**Binary**",
                      "But needs **object detection** first, to crop the biscuits out of the "
                      "raw images. The book notes that *anomaly detection* ==would not fit "
                      "here=="],
                     ["Archaeological sites", "**Image similarity ranking**",
                      "Retrieve images most like known sites."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.1",
            "title": "Two lessons hiding in that table",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🚫", "h": "Some problems are not deep learning problems",
                     "p": "The music recommender is better served by collaborative filtering. "
                          "Recognising that early saves months.", "style": "warn"},
                    {"ico": "🔗", "h": "Some need two models in sequence",
                     "p": "The biscuit case needs detection before classification. Framing it "
                          "as one model would fail quietly.", "style": "warn"},
                ]},
                {"t": "p", "md": "Both are missed routinely when a team jumps straight to "
                                 "modelling."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.1",
            "title": "The two hypotheses you are making silently",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "1️⃣", "h": "Your targets can be predicted from your inputs",
                     "p": "That the relationship exists at all.", "style": "accent"},
                    {"ico": "2️⃣", "h": "Your data is sufficiently informative",
                     "p": "That it is enough to learn that relationship.", "style": "accent"},
                ]},
                {"t": "band", "style": "rose",
                 "md": "Until you have a working model these are **merely hypotheses**. "
                       "Assembling examples of X and targets Y ==does not mean X contains "
                       "enough information to predict Y=="},
                {"t": "p", "md": "The book's example: predicting a stock's movement from its "
                                 "recent price history is **unlikely to succeed**, because "
                                 "price history does not contain much predictive information."},
            ],
            "notes": "Test both hypotheses in the framing meeting, not after three months of "
                     "modelling. This is the single biggest time-saver in the chapter.",
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.1 · ethics",
            "title": "Technology is never neutral",
            "blocks": [
                {"t": "p", "md": "The book places its ethics note **in the framing stage**, "
                                 "not at the end. Its example: *\"building an AI that rates "
                                 "the trustworthiness of someone from a picture of their "
                                 "face\"*."},
                {"t": "steps", "items": [
                    "**The validity is already in doubt** — it is not clear why "
                    "trustworthiness would be reflected in a face.",
                    "Collecting a dataset would amount to **recording the biases and "
                    "prejudices of the people labelling the pictures**.",
                    "A model trained on it would merely **encode those same biases into a "
                    "black-box algorithm** — which gives them a thin veneer of legitimacy.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.1 · ethics",
            "title": "Why the veneer is the dangerous part",
            "blocks": [
                {"t": "quote",
                 "md": "In a largely tech-illiterate society like ours, \"The AI algorithm said "
                       "this person cannot be trusted\" strangely appears to carry more weight "
                       "and objectivity than \"John Smith said this person cannot be trusted\" "
                       "— despite the former being a learned approximation of the latter.",
                 "cite": "Chollet & Watson, section 6.1.1"},
                {"t": "band", "style": "rose",
                 "md": "**Technical choices are also ethical choices.** If your work has any "
                       "impact on the world, that impact has a moral direction — so ==be "
                       "deliberate about the values your work supports=="},
            ],
            "notes": "Easy to make concrete for any audience: eligibility scoring, pricing, "
                     "and customer flagging can all launder historical bias and give it an "
                     "objective face.",
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.2",
            "title": "Collecting data is the expensive part — and the highest-return one",
            "blocks": [
                {"t": "quote",
                 "md": "If you get an extra 50 hours to spend on a project, chances are that "
                       "the most effective way to allocate them is to collect more data, "
                       "rather than search for incremental modeling improvements.",
                 "cite": "Chollet & Watson, section 6.1.2"},
                {"t": "p", "md": "The point that data matters more than algorithms was made "
                                 "most famously in a 2009 Google paper, *\"The Unreasonable "
                                 "Effectiveness of Data\"* — itself a play on Eugene Wigner's "
                                 "1960 title. That predates the popularity of deep learning, "
                                 "and the rise of deep learning has ==only increased the "
                                 "importance of data=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.2",
            "title": "Who should do the annotating",
            "blocks": [
                {"t": "table",
                 "head": ["Option", "Upside", "Risk"],
                 "widths": [26, 36, 38],
                 "rows": [
                     ["**Annotate it yourself**", "Full control over quality.",
                      "Slow and costly in time."],
                     ["**Crowdsourcing** (e.g. Mechanical Turk)", "Inexpensive and scales well.",
                      "Annotations may end up ==quite noisy=="],
                     ["**A specialist labelling company**", "Saves time and money.",
                      "Takes away control."],
                 ]},
                {"t": "p", "md": "Your annotation process determines the quality of your "
                                 "targets, which in turn determines the quality of your model. "
                                 "It deserves the same scrutiny as the architecture."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.2",
            "title": "Three questions that decide which option",
            "blocks": [
                {"t": "bullets", "items": [
                    "**Do the labellers need to be subject-matter experts?** Cat versus dog "
                    "can be done by anyone; dog breeds need specialised knowledge; annotating "
                    "CT scans of fractures ==pretty much requires a medical degree==.",
                    "**If expertise is needed, can you train people?** If not, how will you "
                    "get access to the relevant experts at all?",
                    "**Do you yourself understand how the experts arrive at the annotations?** "
                    "If not, your dataset becomes a black box and manual feature engineering "
                    "is closed to you — not fatal, but limiting.",
                ]},
                {"t": "band",
                 "md": "And decide early what software will record the annotations. Productive "
                       "annotation tooling **saves a great deal of time**, so it is worth "
                       "investing in ==at the start of a project, not the middle=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.2",
            "title": "Non-representative data — the cardinal sin",
            "blocks": [
                {"t": "p", "md": "The book's example: an app that identifies a dish from a "
                                 "photo, trained on pictures from an image-sharing network "
                                 "popular with food enthusiasts. Test accuracy well over 90%."},
                {"t": "band", "style": "rose",
                 "md": "After release: **wrong 8 times out of 10**. User photos — random "
                       "dishes, random restaurants, random phones — ==look nothing like== the "
                       "professional, well-lit, appetising pictures it was trained on."},
                {"t": "bullets", "items": [
                    "Where possible, collect data **directly from the environment the model "
                    "will be used in**.",
                    "A review sentiment model belongs on new IMDB reviews — not Yelp reviews, "
                    "not tweets.",
                    "If training on production data is impossible, **understand exactly how "
                    "they differ** and correct for it actively.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.2",
            "title": "Sampling bias: DEWEY DEFEATS TRUMAN",
            "blocks": [
                {"t": "p", "md": "**Sampling bias** is the subtlest form: your collection "
                                 "process interacts with the thing you are trying to predict."},
                {"t": "p", "md": "On election night in 1948 the *Chicago Tribune* printed the "
                                 "headline **\"DEWEY DEFEATS TRUMAN\"**. By morning Truman had "
                                 "won. The editor had trusted a telephone survey — but "
                                 "telephone users in 1948 ==were not a representative sample "
                                 "of voters==. They were likelier to be richer, more "
                                 "conservative, and to vote for Dewey."},
                {"t": "band", "style": "amber",
                 "md": "Every phone survey now accounts for this. That does not make sampling "
                       "bias a thing of the past — ==only a thing pollsters are now aware "
                       "of=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.2",
            "title": "Concept drift, and how long a model lives",
            "blocks": [
                {"t": "mmd", "id": "ch06-drift", "src": MMD_DRIFT,
                 "cap": "The book's own figures. The most adversarial problem is the one that "
                        "goes stale fastest."},
                {"t": "p", "md": "**Concept drift** is when the properties of production data "
                                 "change over time, gradually degrading the model. The IMDB "
                                 "dataset was collected in 2011; a model trained on it does "
                                 "worse on 2020 reviews than on 2012 ones, because vocabulary, "
                                 "expressions, and genres move."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.2",
            "title": "The assumption underneath every deployed model",
            "blocks": [
                {"t": "band", "style": "rose",
                 "md": "Machine learning can only memorise patterns **present in the training "
                       "data**. Using a model trained on the past to predict the future "
                       "assumes **the future will behave like the past**. ==Often it does "
                       "not.=="},
                {"t": "p", "md": "Handling fast drift requires continuous data collection, "
                                 "annotation, and retraining — which is a staffing decision "
                                 "as much as a technical one."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.3",
            "title": "Understand your data before you model it",
            "blocks": [
                {"t": "p", "md": "Treating a dataset as a black box is **bad practice**. "
                                 "Before training anything, explore and visualise."},
                {"t": "steps", "items": [
                    "Images or text? **Look at a few samples directly**, with their labels.",
                    "Numeric features? **Plot the histograms** to feel the ranges and "
                    "frequencies.",
                    "Location data? **Put it on a map.** Do patterns appear?",
                    "Any **missing values**? They must be handled during preparation.",
                    "A classification task? **Print the count per class.** If it is not "
                    "balanced, that has to be accounted for.",
                    "Check for **target leaks**.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.3",
            "title": "Target leaking, and the one question that catches it",
            "blocks": [
                {"t": "mmd", "id": "ch06-leakcheck", "src": MMD_LEAKCHECK,
                 "cap": "Ask it of every column, not just the suspicious ones."},
                {"t": "p", "md": "The book's example: training on medical records to predict "
                                 "whether someone will be treated for cancer, where the "
                                 "records include the feature *\"this person has been "
                                 "diagnosed with cancer\"*."},
                {"t": "band", "style": "amber",
                 "md": "The common real-world shape: **fields filled in later by an operator** "
                       "— handling status, closure code, follow-up notes. None of them exist "
                       "==at the moment the model has to decide=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.1.4",
            "title": "Choosing a measure of success",
            "blocks": [
                {"t": "quote",
                 "md": "To control something, you need to be able to observe it. To achieve "
                       "success on a project, you must first define what you mean by success.",
                 "cite": "Chollet & Watson, section 6.1.4"},
                {"t": "table",
                 "head": ["Problem shape", "Common metrics"],
                 "widths": [40, 60],
                 "rows": [
                     ["**Balanced** classification", "Accuracy, and **AUC** of the ROC curve."],
                     ["**Imbalanced**, ranking, multilabel",
                      "**Precision and recall**, or a metric counting false/true positives "
                      "and negatives."],
                     ["Neither of the above",
                      "It is not unusual to have to **define your own metric**."],
                 ]},
                {"t": "band",
                 "md": "The metric guides **every technical decision** in the project, so it "
                       "must align directly with the higher-level goal — ==the customer's "
                       "business success=="},
            ],
        },

        {"type": "section", "num": "02", "title": "Developing a model",
         "lead": "The part every tutorial covers — and not the hardest one."},

        {
            "type": "slide",
            "kicker": "Section 6.2.1",
            "title": "Vectorisation and normalisation",
            "blocks": [
                {"t": "p", "md": "Neural networks do not ingest raw data. Whatever you have — "
                                 "sound, images, text — must become float tensors first, and "
                                 "those tensors must have sane ranges."},
                {"t": "code", "lang": "python", "file": "the two properties you want",
                 "src": """# 1. Take small values  - most values in the 0-1 range
# 2. Be homogeneous     - all features on roughly the same scale

# The stricter, common practice:
x -= x.mean(axis=0)     # each feature centred on 0
x /= x.std(axis=0)      # each feature with unit standard deviation"""},
                {"t": "band",
                 "md": "Feeding in large values (multi-digit integers) or heterogeneous ones "
                       "(one feature 0–1, another 100–200) triggers **large gradient updates "
                       "that prevent the network from converging**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.2.1",
            "title": "Missing values: categorical and numerical differ",
            "blocks": [
                {"t": "table",
                 "head": ["Missing value in a…", "What to do"],
                 "widths": [26, 74],
                 "rows": [
                     ["**Categorical** feature",
                      "Safe to create a **new category meaning \"missing\"**. The model will "
                      "learn what that implies about the target on its own."],
                     ["**Numerical** feature",
                      "**Avoid an arbitrary value such as 0** — it can create a discontinuity "
                      "in the latent space. Use the **mean or median**, or train a model to "
                      "predict the value from the other features."],
                 ]},
                {"t": "band", "style": "amber",
                 "md": "A subtle trap: if you **expect** missing categorical values at test "
                       "time but trained on complete data, the network ==never learned to "
                       "ignore them==. Fix it by generating training samples with holes — "
                       "duplicate some rows and drop the fields you expect to lose."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.2.3 – 6.2.5",
            "title": "Model development is three stages, in order",
            "blocks": [
                {"t": "mmd", "id": "ch06-stages", "src": MMD_STAGES,
                 "cap": "Doing them out of order — regularising before you can overfit — "
                        "wastes the most time."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.2.3",
            "title": "Stage 1 — beat a baseline",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🧪", "h": "Feature engineering",
                     "p": "Filter out uninformative features, and use knowledge of the problem "
                          "to build likely-useful new ones.", "style": "accent"},
                    {"ico": "🏛", "h": "The right architecture priors",
                     "p": "Densely connected? ConvNet? Recurrent? Transformer? Or is deep "
                          "learning even the right approach here?", "style": "accent"},
                    {"ico": "🎛", "h": "A good enough training configuration",
                     "p": "Which loss function? What batch size and learning rate?",
                     "style": "accent"},
                ]},
                {"t": "p", "md": "The goal at this stage is **statistical power**: a small "
                                 "model that beats a simple baseline. Nothing more."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.2.3 · table 6.1",
            "title": "The reference table for that third choice",
            "blocks": [
                {"t": "table",
                 "head": ["Task", "Last-layer activation", "Loss function", "Metrics"],
                 "widths": [26, 18, 26, 30],
                 "rows": [
                     ["Binary classification", "Sigmoid", "Binary crossentropy",
                      "Binary accuracy, ROC AUC"],
                     ["Multiclass, single-label", "Softmax", "Categorical crossentropy",
                      "Categorical accuracy, top-k, ROC AUC"],
                     ["Multiclass, multi-label", "Sigmoid", "Binary crossentropy",
                      "Binary accuracy, ROC AUC"],
                     ["Regression", "None", "Mean squared error", "Mean absolute error"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.2.3",
            "title": "Why you optimise a proxy instead of the metric you care about",
            "blocks": [
                {"t": "p", "md": "A loss function must be computable from a single mini-batch "
                                 "— ideally from a single data point — and it must be "
                                 "**differentiable**, or backpropagation cannot run."},
                {"t": "band",
                 "md": "**ROC AUC satisfies neither**, so it cannot be optimised directly. "
                       "In classification we optimise a proxy — usually crossentropy — "
                       "==hoping that as crossentropy falls, ROC AUC rises=="},
                {"t": "p", "md": "For most problems there are existing templates. You are not "
                                 "the first person to build a spam detector or an image "
                                 "classifier, so **research the prior art** before inventing."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.2.4",
            "title": "Stage 2 — scale up until it overfits",
            "blocks": [
                {"t": "p", "md": "Statistical power is not enough. Is the model *powerful "
                                 "enough*? A logistic regression has statistical power on "
                                 "MNIST but cannot solve it well."},
                {"t": "bullets", "items": [
                    "Add layers.",
                    "Make the layers bigger.",
                    "Train for more epochs.",
                ]},
                {"t": "band",
                 "md": "The ideal model sits **exactly on the border** between underfitting "
                       "and overfitting. ==To find where the border is, you must cross it.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.2.5",
            "title": "Stage 3 — regularise and tune",
            "blocks": [
                {"t": "p", "md": "This phase takes the most time: modify, train, evaluate on "
                                 "**validation** data, modify again, and repeat until the "
                                 "model is as good as it will get."},
                {"t": "bullets", "items": [
                    "Try different architectures; add or remove layers.",
                    "Add **dropout**.",
                    "If the model is small, add **L1 or L2 regularisation**.",
                    "Try different hyperparameters — units per layer, learning rate.",
                    "Optionally iterate on **data curation or feature engineering** again.",
                ]},
                {"t": "p", "md": "Much of this can be automated with hyperparameter tuning "
                                 "software such as **KerasTuner** (chapter 18)."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.2.5",
            "title": "The leak that comes back at the end",
            "blocks": [
                {"t": "band", "style": "rose",
                 "md": "Every time you use validation feedback to tune, information leaks into "
                       "the model. A few times is harmless. Done **systematically over many "
                       "iterations**, the model overfits ==to the validation process itself== "
                       "— even though no model was ever trained on validation data."},
                {"t": "p", "md": "So if test performance turns out **significantly worse** "
                                 "than validation performance, either your validation "
                                 "procedure was not reliable, or you overfitted to it. The "
                                 "remedy is a more reliable protocol — **iterated K-fold**."},
            ],
        },

        {"type": "section", "num": "03", "title": "Deploying your model",
         "lead": "A project does not end at a notebook that saves a trained model."},

        {
            "type": "slide",
            "kicker": "Section 6.3.1",
            "title": "Do not say \"98% accurate\"",
            "blocks": [
                {"t": "bullets", "items": [
                    "Non-specialists often expect the system to **understand** its task and "
                    "to exercise human-like common sense.",
                    "The remedy: **show examples of how it fails** — especially "
                    "misclassifications that look surprising.",
                    "Avoid abstract statements like *\"the model is 98% accurate\"*, which "
                    "==most people mentally round up to 100%==.",
                ]},
                {"t": "band",
                 "md": "Speak in **false-negative and false-positive rates**, then translate "
                       "them into daily volumes that a person can picture."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.3.1",
            "title": "What that sounds like in practice",
            "blocks": [
                {"t": "quote",
                 "md": "With these settings, the fraud detection model would have a 5% "
                       "false-negative rate and a 2.5% false-positive rate. Every day, an "
                       "average of 200 valid transactions would be flagged as fraudulent and "
                       "sent for manual review, and an average of 14 fraudulent transactions "
                       "would be missed. An average of 266 fraudulent transactions would be "
                       "correctly caught.",
                 "cite": "The book's own worked example, section 6.3.1"},
                {"t": "band", "style": "amber",
                 "md": "Also discuss the **threshold** with stakeholders. Different thresholds "
                       "give different error rates, and that trade-off ==can only be resolved "
                       "with deep knowledge of the business context=="},
            ],
            "notes": "The most directly usable slide in the chapter. Exercise: have each "
                     "participant rewrite one accuracy claim from their own project in this "
                     "form.",
        },

        {
            "type": "slide",
            "kicker": "Section 6.3.2",
            "title": "Three deployment routes",
            "blocks": [
                {"t": "mmd", "id": "ch06-deploy", "src": MMD_DEPLOY,
                 "cap": "The constraints choose the route, not the other way round."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.3",
            "title": "Reading the tree: what each question is really asking",
            "blocks": [
                {"t": "table",
                 "head": ["Question", "Why it comes first", "Where a yes sends you"],
                 "widths": [26, 46, 28],
                 "rows": [
                     ["**Sensitive data, or poor connectivity?**",
                      "This one outranks the others because it is not a performance "
                      "question. If the data may not leave the device, or there is no "
                      "reliable link, no amount of latency budget changes the answer.",
                      "**On device** — TF Lite, ONNX runtime"],
                     ["**Strict latency requirement?**",
                      "A REST round trip costs roughly 500 ms before your model does "
                      "anything. That is fine for a form submission and useless for "
                      "anything reacting to a camera.",
                      "on to the next question"],
                     ["**Move compute to the user?**",
                      "Running in the browser costs you nothing per request and costs "
                      "the user their battery. It also means shipping the model "
                      "weights, which anyone can then keep.",
                      "**In the browser** — TensorFlow.js, ONNX JS"],
                 ]},
                {"t": "band", "md": "**Every path that answers *no* ends at the REST "
                                    "API**, and that is the right default: one copy of "
                                    "the model, one place to update it, one place to "
                                    "watch. Leave it only when a constraint above "
                                    "forces you to."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.3.2",
            "title": "When each route is the right one",
            "blocks": [
                {"t": "table",
                 "head": ["Route", "Use it when", "Example from the book"],
                 "widths": [18, 50, 32],
                 "rows": [
                     ["**REST API**",
                      "Reliable internet · no strict latency (round trip ≈ **500 ms**) · "
                      "input data is not highly sensitive, since it must be decrypted on the "
                      "server.",
                      "Image search, recommender, fraud detection, satellite imagery."],
                     ["**On device**",
                      "Strict latency or poor connectivity · the model can be made small "
                      "enough · top accuracy is not mission-critical · input data must not be "
                      "decryptable off-device.",
                      "Spam filter inside an end-to-end encrypted chat app; biscuit detection "
                      "at the factory."],
                     ["**In the browser**",
                      "You want to move compute to the user (server costs drop sharply) · data "
                      "must stay on their machine · latency matters · it must work offline "
                      "after download.",
                      "The web and desktop versions of the chat app."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.3.2",
            "title": "One warning about the browser route",
            "blocks": [
                {"t": "band", "style": "rose",
                 "md": "The **entire model is downloaded to the user's device**. Make sure "
                       "nothing about it needs to stay confidential — because given a trained "
                       "model it is usually possible to ==recover some information about its "
                       "training data=="},
                {"t": "p", "md": "Which means: do not publish a model that was trained on "
                                 "sensitive data, however convenient the deployment would be."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.3.2",
            "title": "Exporting: TensorFlow Serving and ONNX",
            "blocks": [
                {"t": "p", "md": "Both work by lifting the weights and the computation graph "
                                 "**out of the Python program**, so the model can be served "
                                 "from a C++ server, a phone, or a browser."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "TensorFlow SavedModel",
                         "src": """model.export("path/to/location",
             format="tf_saved_model")

reloaded = tf.saved_model.load("path/to/location")
predictions = reloaded.serve(input_data)"""},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "ONNX",
                         "src": """model.export("path/to/location",
             format="onnx")

ort_session = onnxruntime.InferenceSession(
    "path/to/location")
predictions = ort_session.run(None, input_data)"""},
                    ],
                ]},
                {"t": "band",
                 "md": "If that sounds like the compilation mechanism from chapter 3, it is: "
                       "TensorFlow Serving is essentially ==a library for serving "
                       "`tf.function` graphs with a saved set of weights=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.3.2",
            "title": "Where those exports run",
            "blocks": [
                {"t": "bullets", "items": [
                    "**TensorFlow Lite** — on-device inference for Android and iOS, ARM CPUs, "
                    "Raspberry Pi, and some microcontrollers. Same save format as TF Serving. "
                    "The ONNX runtime also runs on mobile.",
                    "**TensorFlow.js** — runs in the browser and implements almost the whole "
                    "Keras API (its working name was *WebKeras*). ONNX has its own JavaScript "
                    "runtime.",
                    "**Managed cloud services** such as Cloud AI Platform handle batching, "
                    "load balancing, and scaling for you.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.3.2",
            "title": "Optimising for inference",
            "blocks": [
                {"t": "mmd", "id": "ch06-optimise", "src": MMD_OPTIMISE,
                 "cap": "Both techniques trade a little accuracy for a lot of size and speed."},
                {"t": "p", "md": "**Pruning** drops the coefficients that contribute least; "
                                 "how much you prune is your lever on the size-versus-accuracy "
                                 "trade-off. **Quantization** converts float32 weights to "
                                 "int8, giving a model **four times smaller** that stays near "
                                 "the original accuracy."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.3.2",
            "title": "Quantization is one line",
            "blocks": [
                {"t": "p", "md": "Keras exposes it directly on the model, so it can be applied "
                                 "just before export."},
                {"t": "code", "lang": "python", "file": "the built-in quantize API",
                 "src": """model.quantize("int8")      # compress each weight down to a single byte
model.export("path/to/location", format="onnx")"""},
                {"t": "band",
                 "md": "Do this **before** importing into TensorFlow.js or exporting to "
                       "TensorFlow Lite — it matters most where power and memory are tight, "
                       "==phones and embedded devices=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.3.3",
            "title": "Monitoring: pressing the button is not the end",
            "blocks": [
                {"t": "steps", "items": [
                    "**Randomised A/B testing.** Send a subset of cases through the new model "
                    "and keep a control subset on the old process. Once enough cases have run, "
                    "the difference ==can be attributed to the model== rather than to "
                    "everything else that changed.",
                    "**Regular manual audits** of predictions on production data. Reuse the "
                    "annotation infrastructure: send a fraction out for labelling and compare.",
                    "**When manual audit is impossible**, use alternatives such as user "
                    "surveys — the book's suggestion for the spam and abuse flagging system.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 6.3.4",
            "title": "Maintenance starts on launch day",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "**As soon as your model has launched, you should be getting ready to "
                       "train the next generation that will replace it.**"},
                {"t": "bullets", "items": [
                    "Watch for **changes in production data**. Are new features available? "
                    "Should the label set be expanded or edited?",
                    "Keep collecting and annotating, and **keep improving the annotation "
                    "pipeline** over time.",
                    "Pay special attention to samples the current model finds **difficult** — "
                    "those are ==the ones most likely to improve performance==",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**Define the task first.** Understand the context, the goal, and the "
                    "constraints; collect and annotate data; choose how success is measured.",
                    "You always make **two hypotheses**. Until a model works, neither is proven.",
                    "**Technical choices are ethical choices.** Technology is never neutral.",
                    "**Data must represent production.** Watch for sampling bias, target "
                    "leaks, and concept drift.",
                    "**Beat a baseline → scale up until it overfits → regularise and tune.** "
                    "In that order.",
                    "**Deploy according to the constraints** — API, device, or browser — then "
                    "prune and quantize for inference.",
                    "**Talk in false positives and false negatives**, not percentages of "
                    "accuracy.",
                    "**No model lasts forever.** Monitor, audit, and prepare the successor "
                    "from launch day.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "03_export_and_quantize.ipynb",
                     "href": "../../course-slides/notebooks/ch06/03_export_and_quantize.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 7 — A deep dive on Keras",
                     "href": "../ch07/index.html"},
                ]},
            ],
        },
    ],
}
