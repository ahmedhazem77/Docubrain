# DocuBrain RAG Evaluation Report

Generated: 2026-08-31 10:43:32 UTC

## Overview

- Evaluated document: `finalReport(final).pdf`
- Document ID: **2**
- Workspace ID: **1**
- Number of test questions: **10**
- Overall Faithfulness: **0.9100**
- Overall Answer Relevance: **0.6226**
- Overall Context Recall: **0.6000**
- Average latency: **1884.17 ms**

## Individual Results

| ID | Question | Faithfulness | Answer Relevance | Context Recall | Latency |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | Which imaging modalities does the abstract say deep learning enables automated analysis of? | 1.0000 | 0.9668 | 1.0000 | 1222.53 ms |
| 2 | In the TransUNet decoder, what role do skip connections play? | 1.0000 | 0.9606 | 1.0000 | 1162.68 ms |
| 3 | How many publications does the literature review examine, and how are they divided? | 0.7500 | 0.9079 | 0.0000 | 1536.83 ms |
| 4 | What is the selected primary research article emphasized throughout the report? | 1.0000 | 0.0000 | 0.0000 | 1851.27 ms |
| 5 | According to the experimental results reported for TransUNet, which established CNN-based segmentation methods did the hybrid architecture outperform? | 0.6000 | 0.0000 | 0.0000 | 1979.33 ms |
| 6 | According to Figure 1, what is the progression of deep learning architectures listed before hybrid CNN–Transformer models? | 1.0000 | 0.0000 | 0.0000 | 1151.99 ms |
| 7 | What major challenge related to annotated medical imaging datasets is identified as limiting widespread clinical adoption? | 1.0000 | 0.6232 | 1.0000 | 851.29 ms |
| 8 | What backbone network does the TransUNet CNN encoder use? | 1.0000 | 1.0000 | 1.0000 | 922.14 ms |
| 9 | Which optimizer was used to optimize TransUNet's network parameters during training? | 1.0000 | 0.8139 | 1.0000 | 1952.68 ms |
| 10 | Which two metrics were used to assess TransUNet segmentation performance? | 0.7500 | 0.9540 | 1.0000 | 6211.00 ms |

## Question Details

### Question 1

**Question:** Which imaging modalities does the abstract say deep learning enables automated analysis of?

**Reference answer:** X-ray, computed tomography (CT), magnetic resonance imaging (MRI), ultrasound, and dermoscopy.

**Generated answer:** The abstract states that deep learning enables automated analysis of the following imaging modalities:

- X‑ray  
- Computed tomography (CT)  
- Magnetic resonance imaging (MRI)  
- Ultrasound  
- Dermoscopy

**Latency:** 1222.53 ms

**Faithfulness:** 1.0000  
**Answer Relevance:** 0.9668  
**Context Recall:** 1.0000

**Retrieved contexts:**

1. Abstract
Medical image analysis has become an essential component of modern
healthcare by assisting clinicians in the early detection, diagnosis, and
treatment of various diseases. Recent advances in deep learning have sig-
nificantly improved the accuracy and efficiency of medical image interpre-
tation, enabling automated analysis of imaging modalities such as X-ray,
computed tomography (CT), magnetic resonance imaging (MRI), ultra-
sound, and dermoscopy. This literature review investigates the effective-
ness of deep learning techniques in medical image analysis by examining
fifteen selected publications, including five review papers and ten original
research articles. The review covers major deep learning architectures, in-

2. inical decision-making.
However, manual image analysis is often time-consuming, requires highly spe-cialized expertise, and is subject to inter-observer variability, making consistent
diagnosis challenging in large-scale clinical settings.
Recent advances in artificial intelligence (AI), particularly deep learning,
have transformed the field of medical image analysis by enabling automated
feature extraction and end-to-end learning directly from medical images. Unlike
conventional machine learning methods that rely on handcrafted features, deep
learning models automatically learn hierarchical representations from raw image
data, allowing them to achieve remarkable performance across various medical
imaging tasks. Convolutional Neural Networks (CNNs) have become the foun-
dation of many successful medical image analysis systems due to their ability

3. 2 Literature Review
2.1 Overview of the Selected Literature
Deep learning has emerged as one of the most transformative technologies in
medical image analysis, enabling substantial improvements in disease diagnosis,
image segmentation, lesion detection, and clinical decision support. Advances
in neural network architectures have shifted medical imaging from traditional
handcrafted feature extraction toward automated hierarchical feature learning,
allowing models to identify complex visual patterns directly from medical im-
ages. Consequently, deep learning has achieved state-of-the-art performance
across numerous imaging modalities, including computed tomography (CT),
magnetic resonance imaging (MRI), X-ray, retinal fundus imaging, dermoscopy,

4. ses major challenges lim-
iting the widespread clinical adoption of deep learning, including limitedannotated datasets, domain shift, computational complexity, and the lack
of model interpretability. Emerging research directions, such as explain-
able artificial intelligence (XAI), multimodal learning, foundation models,
and self-supervised learning, are also examined as promising solutions for
improving the robustness, generalizability, and clinical applicability of in-
telligent medical imaging systems. Overall, this report provides a compre-
hensive overview of current advances in deep learning for medical image
analysis while highlighting the contributions of the selected research ar-
ticle and identifying future opportunities for developing more accurate,
reliable, and clinically deployable artificial intelligence solutions.
2

### Question 2

**Question:** In the TransUNet decoder, what role do skip connections play?

**Reference answer:** They combine high-resolution features from the CNN encoder with the corresponding decoder features and preserve fine anatomical details that might otherwise be lost during feature extraction.

**Generated answer:** In the TransUNet decoder, skip connections link the high‑resolution feature maps produced by the CNN encoder to the corresponding stages of the decoder. By doing so, they **preserve fine‑grained spatial (anatomical) details** that might be lost during the deep encoding process, while also allowing the decoder to **leverage the global contextual information** learned by the Transformer encoder. This combination of detailed local features with the globally‑aware decoder representations helps the model reconstruct accurate segmentation maps.

**Latency:** 1162.68 ms

**Faithfulness:** 1.0000  
**Answer Relevance:** 0.9606  
**Context Recall:** 1.0000

**Retrieved contexts:**

1. 2: Overview of the TransUNet architecture proposed by
[Chen et al., 2024]
3.2 TransUNet ArchitectureTransUNet extends the conventional U-Net architecture by integrating a Vision
Transformer (ViT) into the encoder, enabling the model to capture both local
12

2.  . . . 10
2.6 Research Objective of the Selected Paper . . . . . . . . . . . . . 11
3 Methodology 123.1 Overview of the Proposed Method . . . . . . . . . . . . . . . . . 12
3.2 TransUNet Architecture . . . . . . . . . . . . . . . . . . . . . . . 12
3.2.1 CNN Encoder . . . . . . . . . . . . . . . . . . . . . . . . . 13
3.2.2 Vision Transformer Encoder . . . . . . . . . . . . . . . . . 13
3.2.3 Decoder and Skip Connections . . . . . . . . . . . . . . . 13
3.2.4 Segmentation Output . . . . . . . . . . . . . . . . . . . . 14
3.3 Training Procedure . . . . . . . . . . . . . . . . . . . . . . . . . . 14
3.4 Experimental Evaluation . . . . . . . . . . . . . . . . . . . . . . . 15
4 Results and Discussion 16
4.1 Experimental Results . . . . . . . . . . . . . . . . . . . . . . . . . 16
4.2 Comparison with Existing Methods . . . . . . . . . . . . . . . . . 17

3. cts low-level spatial fea-
tures from the input image, whereas the Transformer encoder models globalcontextual relationships through self-attention. These complementary repre-
sentations are subsequently combined within a U-Net-style decoder using skip
connections to reconstruct accurate segmentation maps.
The proposed methodology was evaluated on multiple public benchmark
datasets and compared with several state-of-the-art segmentation methods. The
reported experimental results demonstrate that integrating CNNs with Trans-
formers improves segmentation performance across different medical imaging
modalities. The following sections describe the architecture, training procedure,
and evaluation methodology adopted in the selected paper.
Figure 2: Overview of the TransUNet architecture proposed by
[Chen et al., 2024]
3.2 TransUNet Architecture

4. ogressively upsampling
the encoded feature representations. At each decoding stage, skip connectionscombine high-resolution features extracted by the CNN encoder with the corre-
sponding decoder features.
These skip connections preserve fine anatomical details that may otherwise
be lost during feature extraction while allowing the decoder to benefit from
the global contextual information learned by the Transformer encoder. Con-
sequently, the hybrid architecture achieves accurate localization together with
robust semantic understanding.
13

### Question 3

**Question:** How many publications does the literature review examine, and how are they divided?

**Reference answer:** Fifteen selected publications, including five review papers and ten original research articles.

**Generated answer:** The literature review examines **nine publications**.  
They are divided into two groups:

* **Review articles:** 5 (Jiang et al., 2023; Salehi et al., 2023; Takahashi et al., 2024; Sadeghi et al., 2024; Asgari Taghanaki et al., 2021)  
* **Research articles:** 4 (Esteva et al., 2017; Gargeya and Leng, 2017; Apostolopoulos and Mpesiana, 2020; Frid‑Adar et al., 2018)

**Latency:** 1536.83 ms

**Faithfulness:** 0.7500  
**Answer Relevance:** 0.9079  
**Context Recall:** 0.0000

**Retrieved contexts:**

1. . . . . . . . . . . . . 16
4.2 Comparison with Existing Methods . . . . . . . . . . . . . . . . . 174.3 Discussion . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
5 Conclusion and F uture W ork 18
1

2. Table 1: Summary of the Selected Literature
Reference Type Primary Method Medical Application
[Jiang et al., 2023] Review Deep Learning Archi-
tectures
Cancer diagnosis
[Salehi et al., 2023] Review CNNs and Transfer
Learning
General medical imaging
[Takahashi et al., 2024] Review Vision Transformers Medical image analysis
[Sadeghi et al., 2024] Review Explainable AI
(XAI)
Clinical decision support
[Asgari Taghanaki et al., 2021] Review Semantic Segmenta-
tion
Medical image segmentation
[Esteva et al., 2017] Research CNN Skin cancer classification
[Gargeya and Leng, 2017] Research Deep CNN Diabetic retinopathy detection
[Apostolopoulos and Mpesiana, 2020] Research Transfer Learning COVID-19 detection
[Frid-Adar et al., 2018] Research GAN Liver lesion classification

3. ical practice. These
challenges include limited availability of high-quality annotated datasets, do-main shift between institutions, computational complexity, model interpretabil-
3

4. appropriate rep-
resentative of recent developments in deep learning-based medical image analy-
sis.Having established the research context through the reviewed literature, the
following chapter examines the methodology proposed by [Chen et al., 2024] in
detail, focusing on the TransUNet architecture, training procedure, and exper-
imental evaluation.
11

### Question 4

**Question:** What is the selected primary research article emphasized throughout the report?

**Reference answer:** TransUNet: Rethinking the U-Net Architecture Design for Medical Image Segmentation Through the Lens of Transformers

**Generated answer:** The retrieved excerpt does not identify a single “selected primary research article” that is emphasized throughout the report. It lists several primary research studies in Table 1—​e.g., Esteva et al., 2017 (CNN skin‑cancer classification), Gargeya and Leng, 2017 (deep CNN diabetic‑retinopathy detection), Apostolopoulos and Mpesiana, 2020 (transfer‑learning COVID‑19 detection), and Frid‑Adar et al., 2018 (GAN liver‑lesion classification)—but it does not single out one of them as the focal primary article. Therefore, the specific primary research article emphasized in the report cannot be determined from the provided context.

**Latency:** 1851.27 ms

**Faithfulness:** 1.0000  
**Answer Relevance:** 0.0000  
**Context Recall:** 0.0000

**Retrieved contexts:**

1. . . . . . . . . . . . . 16
4.2 Comparison with Existing Methods . . . . . . . . . . . . . . . . . 174.3 Discussion . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
5 Conclusion and F uture W ork 18
1

2. Contents
1 Introduction 3
1.1 Background . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
1.2 Motivation and Practical Applications . . . . . . . . . . . . . . . 3
1.3 Problem Statement . . . . . . . . . . . . . . . . . . . . . . . . . . 4
2 Literature Review 5
2.1 Overview of the Selected Literature . . . . . . . . . . . . . . . . . 5
2.2 Evolution of Deep Learning Architectures . . . . . . . . . . . . . 6
2.3 Emerging Learning Strategies . . . . . . . . . . . . . . . . . . . . 8
2.4 Applications of Deep Learning in Medical Imaging . . . . . . . . 9
2.5 Current Challenges and Future Research Directions . . . . . . . . 10
2.6 Research Objective of the Selected Paper . . . . . . . . . . . . . 11
3 Methodology 12

3. ical practice. These
challenges include limited availability of high-quality annotated datasets, do-main shift between institutions, computational complexity, model interpretabil-
3

4. Table 1: Summary of the Selected Literature
Reference Type Primary Method Medical Application
[Jiang et al., 2023] Review Deep Learning Archi-
tectures
Cancer diagnosis
[Salehi et al., 2023] Review CNNs and Transfer
Learning
General medical imaging
[Takahashi et al., 2024] Review Vision Transformers Medical image analysis
[Sadeghi et al., 2024] Review Explainable AI
(XAI)
Clinical decision support
[Asgari Taghanaki et al., 2021] Review Semantic Segmenta-
tion
Medical image segmentation
[Esteva et al., 2017] Research CNN Skin cancer classification
[Gargeya and Leng, 2017] Research Deep CNN Diabetic retinopathy detection
[Apostolopoulos and Mpesiana, 2020] Research Transfer Learning COVID-19 detection
[Frid-Adar et al., 2018] Research GAN Liver lesion classification

### Question 5

**Question:** According to the experimental results reported for TransUNet, which established CNN-based segmentation methods did the hybrid architecture outperform?

**Reference answer:** U-Net and Attention U-Net.

**Generated answer:** The retrieved excerpts do not specify the particular CNN‑based segmentation methods that TransUNet outperformed in the experimental results. They only note that TransUNet was compared with several state‑of‑the‑art methods and that it improves upon traditional CNN models such as U‑Net, but no specific CNN‑based methods are listed. Therefore, the requested information could not be found in the provided document context.

**Latency:** 1979.33 ms

**Faithfulness:** 0.6000  
**Answer Relevance:** 0.0000  
**Context Recall:** 0.0000

**Retrieved contexts:**

1. cts low-level spatial fea-
tures from the input image, whereas the Transformer encoder models globalcontextual relationships through self-attention. These complementary repre-
sentations are subsequently combined within a U-Net-style decoder using skip
connections to reconstruct accurate segmentation maps.
The proposed methodology was evaluated on multiple public benchmark
datasets and compared with several state-of-the-art segmentation methods. The
reported experimental results demonstrate that integrating CNNs with Trans-
formers improves segmentation performance across different medical imaging
modalities. The following sections describe the architecture, training procedure,
and evaluation methodology adopted in the selected paper.
Figure 2: Overview of the TransUNet architecture proposed by
[Chen et al., 2024]
3.2 TransUNet Architecture

2. Figure 3: Qualitative segmentation results produced by TransUNet dur-
ing successive coarse-to-fine refinement stages. The predicted segmentation
masks become progressively closer to the ground-truth annotations, demon-
strating the effectiveness of the proposed refinement strategy. Adapted from
[Chen et al., 2024]
4.2 Comparison with Existing Methods
The superior performance of TransUNet can be attributed to its hybrid architec-
ture, which combines the complementary strengths of convolutional neural net-
works and Vision Transformers. Traditional CNN-based models, such as U-Net,
are highly effective at extracting local spatial features but often struggle to cap-
ture long-range dependencies within medical images. Conversely, Transformer-

3. 3 Methodology
3.1 Overview of the Proposed Method
The selected paper proposes TransUNet, a hybrid deep learning architecture
designed for medical image segmentation. The primary objective of the model
is to overcome the limitations of conventional convolutional neural networks
(CNNs) in capturing long-range contextual information while preserving the
precise localization capabilities required for pixel-level segmentation.
Unlike traditional U-Net architectures that rely solely on convolutional op-
erations, TransUNet integrates a Vision Transformer (ViT) encoder within the
segmentation framework. The CNN component extracts low-level spatial fea-
tures from the input image, whereas the Transformer encoder models global

4. vised deep learning
approaches, the model relies on large quantities of accurately annotated medicalimages, which are often expensive and time-consuming to obtain.
Overall, the findings indicate that TransUNet successfully combines the
strengths of convolutional neural networks and Vision Transformers to overcome
many of the limitations associated with traditional segmentation methods. The
proposed hybrid architecture establishes a strong foundation for future research
on efficient Transformer-based models capable of delivering accurate and reliable
medical image segmentation in clinical practice.
5 Conclusion and Future Work
This report reviewed the application of deep learning techniques in medical
image analysis, with particular emphasis on the selected paper,TransUNet:
Rethinking the U-Net Architecture Design Through the Lens of Transformers

### Question 6

**Question:** According to Figure 1, what is the progression of deep learning architectures listed before hybrid CNN–Transformer models?

**Reference answer:** Traditional Machine Learning, CNN-based Models, Transfer Learning, and Vision Transformers, followed by Hybrid CNN–Transformer Models (MultiResUNet → TransUNet → HiFuse).

**Generated answer:** The retrieved excerpts do not contain a description of Figure 1 or list the deep‑learning architectures that appear in it prior to the hybrid CNN–Transformer models. Therefore, the specific progression of architectures shown in Figure 1 cannot be determined from the provided document context.

**Latency:** 1151.99 ms

**Faithfulness:** 1.0000  
**Answer Relevance:** 0.0000  
**Context Recall:** 0.0000

**Retrieved contexts:**

1. ows [Sadeghi et al., 2024].
The increasing complexity of modern architectures also introduces compu-tational challenges. Vision Transformers and hybrid CNN–Transformer models
generally require greater computational resources and larger training datasets
than conventional convolutional networks. These requirements may limit their
deployment in resource-constrained healthcare settings, particularly in low- and
middle-income countries where computing infrastructure is limited [Takahashi et al., 2024,
Chen et al., 2024].
Future research is expected to focus on developing more data-efficient, in-
10

2. vised deep learning
approaches, the model relies on large quantities of accurately annotated medicalimages, which are often expensive and time-consuming to obtain.
Overall, the findings indicate that TransUNet successfully combines the
strengths of convolutional neural networks and Vision Transformers to overcome
many of the limitations associated with traditional segmentation methods. The
proposed hybrid architecture establishes a strong foundation for future research
on efficient Transformer-based models capable of delivering accurate and reliable
medical image segmentation in clinical practice.
5 Conclusion and Future Work
This report reviewed the application of deep learning techniques in medical
image analysis, with particular emphasis on the selected paper,TransUNet:
Rethinking the U-Net Architecture Design Through the Lens of Transformers

3.  selected paper,TransUNet:
Rethinking the U-Net Architecture Design Through the Lens of Transformers[Chen et al., 2024]. The reviewed literature demonstrated the remarkable progress
of deep learning over the past decade, highlighting the transition from conven-
tional convolutional neural networks to more advanced hybrid CNN–Transformer
architectures. These developments have significantly improved the performance
of medical image analysis tasks, including image classification, segmentation,
disease detection, and computer-aided diagnosis, thereby supporting more ac-
curate and efficient clinical decision-making.
The selected paper introduced TransUNet, a hybrid framework that com-
bines the local feature extraction capabilities of convolutional neural networks
with the global contextual modeling provided by Vision Transformers. By in-
18

4. gress in medical image
analysis through advances in convolutional neural networks, Vision Transform-ers, hybrid architectures, and emerging learning strategies. Although these
approaches have significantly improved diagnostic accuracy and segmentation
performance, challenges related to balancing local feature extraction with global
contextual understanding remain. These limitations have motivated the devel-
opment of hybrid architectures that combine the complementary strengths of
CNNs and Vision Transformers.
Among the reviewed studies,TransUNet: Rethinking the U-Net Architecture
Design Through the Lens of Transformers[Chen et al., 2024] was selected as the
primary paper because it represents a significant advancement in medical image
segmentation. By integrating convolutional neural networks with Transformer-

### Question 7

**Question:** What major challenge related to annotated medical imaging datasets is identified as limiting widespread clinical adoption?

**Reference answer:** The scarcity of large, high-quality annotated medical imaging datasets.

**Generated answer:** The report identifies the **scarcity / limited availability of large, high‑quality annotated medical imaging datasets** as a major challenge that hinders the widespread clinical adoption of deep‑learning systems.

**Latency:** 851.29 ms

**Faithfulness:** 1.0000  
**Answer Relevance:** 0.6232  
**Context Recall:** 1.0000

**Retrieved contexts:**

1. nguage
learning
[Tiu et al., 2022] Zero-shot chest X-ray interpreta-
tion using image–text learning.2.5 Current Challenges and Future Research Directions
Despite the remarkable progress of deep learning in medical image analysis, sev-
eral challenges continue to hinder its widespread adoption in clinical practice.
One of the most significant limitations is the scarcity of large, high-quality anno-
tated medical imaging datasets [Jiang et al., 2023, Salehi et al., 2023]. Obtain-
ing expert annotations is both time-consuming and expensive, while concerns
regarding patient privacy and data sharing further restrict the availability of di-
verse training data. Consequently, many deep learning models are trained on rel-
atively small datasets, limiting their ability to generalize across different health-
care institutions and patient populations [Jiang et al., 2023, Salehi et al., 2023].

2. 9 diagnosis from chest
X-rays, organ segmentation, and tumor localization. In addition, emerging ap-proaches such as self-supervised learning and multimodal learning aim to reduce
dependence on large annotated datasets while improving model generalization
across different imaging modalities and clinical environments.
1.2 Motivation and Practical Applications
The increasing volume and complexity of medical imaging data have created a
growing demand for intelligent systems capable of assisting healthcare profes-
sionals in image interpretation. Although deep learning models have demon-
strated remarkable accuracy in controlled research settings, several challenges
continue to limit their widespread adoption in real-world clinical practice. These
challenges include limited availability of high-quality annotated datasets, do-

3. ses major challenges lim-
iting the widespread clinical adoption of deep learning, including limitedannotated datasets, domain shift, computational complexity, and the lack
of model interpretability. Emerging research directions, such as explain-
able artificial intelligence (XAI), multimodal learning, foundation models,
and self-supervised learning, are also examined as promising solutions for
improving the robustness, generalizability, and clinical applicability of in-
telligent medical imaging systems. Overall, this report provides a compre-
hensive overview of current advances in deep learning for medical image
analysis while highlighting the contributions of the selected research ar-
ticle and identifying future opportunities for developing more accurate,
reliable, and clinically deployable artificial intelligence solutions.
2

4. medical images, transfer
learning became a widely adopted strategy. Rather than training models fromscratch, networks pre-trained on large natural image datasets are fine-tuned for
specific medical imaging tasks. This approach significantly improves model per-
formance while reducing training time and annotation requirements. The effec-
6

### Question 8

**Question:** What backbone network does the TransUNet CNN encoder use?

**Reference answer:** ResNet-50.

**Generated answer:** The TransUNet CNN encoder uses a **ResNet‑50** backbone network.

**Latency:** 922.14 ms

**Faithfulness:** 1.0000  
**Answer Relevance:** 1.0000  
**Context Recall:** 1.0000

**Retrieved contexts:**

1. 2: Overview of the TransUNet architecture proposed by
[Chen et al., 2024]
3.2 TransUNet ArchitectureTransUNet extends the conventional U-Net architecture by integrating a Vision
Transformer (ViT) into the encoder, enabling the model to capture both local
12

2. 3.2.4 Segmentation Output
The final decoder layer produces a pixel-wise probability map representing the
predicted segmentation of the target anatomical structure. During inference,
each pixel is assigned to the class with the highest predicted probability, result-
ing in the final segmentation mask.
This hybrid encoder-decoder design enables TransUNet to outperform many
conventional CNN-based segmentation models by effectively combining local
feature extraction with long-range contextual modeling.
Table 3: Main Components of the TransUNet Architecture
Component Purpose
CNN Encoder (ResNet-
50)
Extracts hierarchical local image features from the input image.
Patch Embedding Converts CNN feature maps into a sequence of token embeddings
for Transformer processing.
Vision Transformer En-

3. spatial features and global contextual information. As illustrated in Figure 3,
the framework consists of three main components: a CNN encoder for local
feature extraction, a Transformer encoder for global context modeling, and a
decoder with skip connections for precise image segmentation. This hybrid
design combines the strengths of convolutional networks and Transformers while
preserving the encoder–decoder structure that has become the standard for
medical image segmentation.
3.2.1 CNN Encoder
The first stage of TransUNet employs a convolutional neural network to extract
low-level image features. Specifically, a ResNet-50 backbone is used to learn hi-
erarchical feature representations such as edges, textures, and anatomical struc-

4. cts low-level spatial fea-
tures from the input image, whereas the Transformer encoder models globalcontextual relationships through self-attention. These complementary repre-
sentations are subsequently combined within a U-Net-style decoder using skip
connections to reconstruct accurate segmentation maps.
The proposed methodology was evaluated on multiple public benchmark
datasets and compared with several state-of-the-art segmentation methods. The
reported experimental results demonstrate that integrating CNNs with Trans-
formers improves segmentation performance across different medical imaging
modalities. The following sections describe the architecture, training procedure,
and evaluation methodology adopted in the selected paper.
Figure 2: Overview of the TransUNet architecture proposed by
[Chen et al., 2024]
3.2 TransUNet Architecture

### Question 9

**Question:** Which optimizer was used to optimize TransUNet's network parameters during training?

**Reference answer:** The Adam optimizer.

**Generated answer:** The TransUNet model was trained using the **Adam optimizer** to optimize its network parameters.

**Latency:** 1952.68 ms

**Faithfulness:** 1.0000  
**Answer Relevance:** 0.8139  
**Context Recall:** 1.0000

**Retrieved contexts:**

1. 2: Overview of the TransUNet architecture proposed by
[Chen et al., 2024]
3.2 TransUNet ArchitectureTransUNet extends the conventional U-Net architecture by integrating a Vision
Transformer (ViT) into the encoder, enabling the model to capture both local
12

2. The performance of TransUNet was assessed using standard medical im-
age segmentation metrics, including the Dice Similarity Coefficient (DSC) and
the 95% Hausdorff Distance (HD95). These metrics evaluate both the overlap
between predicted and reference segmentation masks and the accuracy of the
predicted object boundaries, providing a comprehensive assessment of segmen-
tation quality.
Table 4: Summary of the Training Procedure Used in TransUNet
T raining Aspect Description
Learning Strategy Supervised learning using manually annotated segmentation
masks.
Optimizer Adam optimizer for parameter optimization.
Weight Initialization CNN encoder initialized with ImageNet pre-trained weights;
Transformer initialized using transfer learning.

3. oder initialized with ImageNet pre-trained weights;
Transformer initialized using transfer learning.Data Augmentation Random rotations, flipping, and scaling to improve model gener-
alization.
Evaluation Metrics Dice Similarity Coefficient (DSC) and 95% Hausdorff Distance
(HD95).
3.4 Experimental Evaluation
To validate the effectiveness of the proposed architecture, [Chen et al., 2024]conducted
extensive experiments on multiple publicly available medical image segmen-
tation benchmarks. The evaluation included datasets representing different
anatomical structures and imaging modalities, enabling a comprehensive as-
sessment of the model’s generalization capability.
The performance of TransUNet was compared with several state-of-the-art
segmentation methods, including conventional U-Net variants, attention-based
networks, and Transformer-based architectures. All competing models were

4.  . . . 10
2.6 Research Objective of the Selected Paper . . . . . . . . . . . . . 11
3 Methodology 123.1 Overview of the Proposed Method . . . . . . . . . . . . . . . . . 12
3.2 TransUNet Architecture . . . . . . . . . . . . . . . . . . . . . . . 12
3.2.1 CNN Encoder . . . . . . . . . . . . . . . . . . . . . . . . . 13
3.2.2 Vision Transformer Encoder . . . . . . . . . . . . . . . . . 13
3.2.3 Decoder and Skip Connections . . . . . . . . . . . . . . . 13
3.2.4 Segmentation Output . . . . . . . . . . . . . . . . . . . . 14
3.3 Training Procedure . . . . . . . . . . . . . . . . . . . . . . . . . . 14
3.4 Experimental Evaluation . . . . . . . . . . . . . . . . . . . . . . . 15
4 Results and Discussion 16
4.1 Experimental Results . . . . . . . . . . . . . . . . . . . . . . . . . 16
4.2 Comparison with Existing Methods . . . . . . . . . . . . . . . . . 17

### Question 10

**Question:** Which two metrics were used to assess TransUNet segmentation performance?

**Reference answer:** The Dice Similarity Coefficient (DSC) and the 95% Hausdorff Distance (HD95).

**Generated answer:** The segmentation performance of TransUNet was evaluated using two metrics:

1. **Dice Similarity Coefficient (DSC)** – measures the overlap between the predicted and reference segmentation masks.  
2. **95% Hausdorff Distance (HD95)** – assesses the accuracy of the predicted object boundaries.

These metrics are mentioned throughout the retrieved document (e.g., pages 16‑17).

**Latency:** 6211.00 ms

**Faithfulness:** 0.7500  
**Answer Relevance:** 0.9540  
**Context Recall:** 1.0000

**Retrieved contexts:**

1. The performance of TransUNet was assessed using standard medical im-
age segmentation metrics, including the Dice Similarity Coefficient (DSC) and
the 95% Hausdorff Distance (HD95). These metrics evaluate both the overlap
between predicted and reference segmentation masks and the accuracy of the
predicted object boundaries, providing a comprehensive assessment of segmen-
tation quality.
Table 4: Summary of the Training Procedure Used in TransUNet
T raining Aspect Description
Learning Strategy Supervised learning using manually annotated segmentation
masks.
Optimizer Adam optimizer for parameter optimization.
Weight Initialization CNN encoder initialized with ImageNet pre-trained weights;
Transformer initialized using transfer learning.

2. 4 Results and Discussion
4.1 Experimental Results
The experimental results reported by [Chen et al., 2024] demonstrate that Tran-
sUNet consistently achieves high segmentation accuracy across multiple medical
imaging benchmark datasets. The proposed hybrid architecture outperformed
several established convolutional neural network-based methods, including U-
Net and Attention U-Net, while also achieving competitive performance against
other Transformer-based segmentation models.
Performance was primarily evaluated using the Dice Similarity Coefficient
(DSC), where higher values indicate greater agreement between the predicted
segmentation and the ground-truth annotation. In addition, the 95% Haus-
dorff Distance (HD95) was used to assess boundary accuracy, with lower values

3. oder initialized with ImageNet pre-trained weights;
Transformer initialized using transfer learning.Data Augmentation Random rotations, flipping, and scaling to improve model gener-
alization.
Evaluation Metrics Dice Similarity Coefficient (DSC) and 95% Hausdorff Distance
(HD95).
3.4 Experimental Evaluation
To validate the effectiveness of the proposed architecture, [Chen et al., 2024]conducted
extensive experiments on multiple publicly available medical image segmen-
tation benchmarks. The evaluation included datasets representing different
anatomical structures and imaging modalities, enabling a comprehensive as-
sessment of the model’s generalization capability.
The performance of TransUNet was compared with several state-of-the-art
segmentation methods, including conventional U-Net variants, attention-based
networks, and Transformer-based architectures. All competing models were

4. cts low-level spatial fea-
tures from the input image, whereas the Transformer encoder models globalcontextual relationships through self-attention. These complementary repre-
sentations are subsequently combined within a U-Net-style decoder using skip
connections to reconstruct accurate segmentation maps.
The proposed methodology was evaluated on multiple public benchmark
datasets and compared with several state-of-the-art segmentation methods. The
reported experimental results demonstrate that integrating CNNs with Trans-
formers improves segmentation performance across different medical imaging
modalities. The following sections describe the architecture, training procedure,
and evaluation methodology adopted in the selected paper.
Figure 2: Overview of the TransUNet architecture proposed by
[Chen et al., 2024]
3.2 TransUNet Architecture

## Poor Performers

- Question 3: faithfulness=0.7500, answer_relevancy=0.9079, context_recall=0.0000
- Question 4: faithfulness=1.0000, answer_relevancy=0.0000, context_recall=0.0000
- Question 5: faithfulness=0.6000, answer_relevancy=0.0000, context_recall=0.0000
- Question 6: faithfulness=1.0000, answer_relevancy=0.0000, context_recall=0.0000
- Question 7: faithfulness=1.0000, answer_relevancy=0.6232, context_recall=1.0000
