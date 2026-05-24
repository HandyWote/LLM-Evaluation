# 分歧核查表

对每个分歧字段，看定义和证据后，在「判定」写 cxt / hyh / 其他，在「理由」简要说明。

---
## Paper 1　（1 个分歧）

### Eval_Automatic
**定义**: 算法/数学公式自动计算的指标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The therapist's replies are evaluated from three aspects (empathy, logical coherence, and guidance) and an overall score Larsson et al. (2016), with each evaluation metric score ranging from 0 to 3.
**cxt 补充证据**: "Regarding the AI therapists, we employ a dual approach for evaluation: manual and automated assessments. Our domain expert co-authors design

**判定**: ___　　**理由**: ___

---
## Paper 6　（2 个分歧）

### Eval_Lay_Users
**定义**: 非专家/普通用户进行评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We first conduct an expert evaluation with 2 licensed clinical psychologists. The 2 clinicians have backgrounds in adult psychology, specializing in depression, anxiety disorders and cognitive behavior therapy (CBT).
**cxt 补充证据**: We set up a randomized controlled experiment using Amazon Mechanical Turk to crowdsource peer-to-peer support responses… Each Mechanical Turk worker is shown a post and asked to provide a response, as if responding to a friend.”

**判定**: ___　　**理由**: ___

### Prompt_Disclosure
**定义**: 提示词披露度: Full（清晰提供了所有必要提示词，原则上可复现）/ Partial（展示了部分提示词，不足以复现）/ No（没有可用的提示词信息）

| cxt | hyh |
|-----|-----|
| FULL | PARTIAL |

**eval_report 证据**: For GPT-4 response, we test 3 different treatment persona settings in total:
**cxt 补充证据**: "“An example SMP persona prompt is shown below:

**判定**: ___　　**理由**: ___

---
## Paper 10　（1 个分歧）

### Fidelity
**定义**: 是否符合预设角色/目标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: evaluation framework based on three key criteria:
**cxt 补充证据**: We leverage the powerful in-context learning ability of LLMs to generate therapeutic interventions without explicit fine-tuning.”

**判定**: ___　　**理由**: ___

---
## Paper 13　（2 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| DYNAMIC | STATIC |

**eval_report 证据**: Each User Agent undergoes a self-mental health assessment using the psychometric tools (see Section 3.1.3) to establish an initial mental status. ... Following the interaction, the user agent reassesses its mental health state using the same tools applied during initialization.
**cxt 补充证据**: “The simulated patient engages in structured, topic-driven conversations with a Character-based Agent persona. Each conversation is segmented into well-defined topics, with a maximum of 10 dialogue turns per topic… During the conversation, once a topic exceeds three conversational turns, the Dialog Manager Agent begins to evaluate user messages after each turn to ensure ongoing relevance and resol

**判定**: ___　　**理由**: ___

### Uses_Dynamic_State
**定义**: 是否使用动态状态建模（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Each User Agent undergoes a self-mental health assessment using the psychometric tools (see Section 3.1.3) to establish an initial mental status. ... Following the interaction, the user agent reassesses its mental health state using the same tools applied during initialization.
**cxt 补充证据**: The Safeguard Agent analyzes conversations after every three dialogue turns, providing structured feedback to refine Character-based Agent’s responses and mitigate potential risks.

**判定**: ___　　**理由**: ___

---
## Paper 15　（3 个分歧）

### Eval_LLM_Judge
**定义**: 使用大模型进行打分、比较、排序（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Our work addresses this gap by using LLMs to automate PST annotation, using both closed- and open-source models to categorize therapist utterances.
**cxt 补充证据**: “We prompted GPT-4o to analyze therapeutic dynamics in each therapist utterance (see Appendix C.2).

**判定**: ___　　**理由**: ___

### Fidelity
**定义**: 是否符合预设角色/目标（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: Using this approach, we compared the efficiency and accuracy of these models against our 500 annotated utterances. ... GPT-4o outperformed all models, achieving the highest accuracy (0.76) in identifying all strategies.
**cxt 补充证据**: does not endorse the use of LLMs in therapeutic settings, nor does it claim that they are ready for such applications.”

**判定**: ___　　**理由**: ___

### LLM_Judge_Validated
**定义**: LLM裁判是否经过验证（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Our work addresses this gap by using LLMs to automate PST annotation, using both closed- and open-source models to categorize therapist utterances.
**cxt 补充证据**: We used Cohen’s Kappa to assess annotators’ agreement across different classes of PST strategies. Our findings show that the agreement scores ranged from 0.69 to 0.88 for strategies in our codebook, indicating substantial agreement.

**判定**: ___　　**理由**: ___

---
## Paper 18　（6 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| DYNAMIC | STATIC |

**eval_report 证据**: We evaluate the consistency of the simulator's utterances with those of real seekers as an evaluation of anthropomorphism using the BERT-score (Zhang et al., 2020). ... The final personality fidelity of the virtual seekers created by each method is obtained from Equation (5).

**判定**: ___　　**理由**: ___

### Eval_Human_Experts
**定义**: 领域专家（治疗师、临床医生、受过训练的标注员）进行评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We quantitatively compare the performance of different methods in seeker simulation by evaluating the behavioral consistency between simulators and real seekers from different perspectives.
**cxt 补充证据**: We invite three experts with a background in psychology to review the data. They are first asked to mark whether the chain of chief complaints was reasonable or not based on seekers’ profiles, counselors’ reports, and conversations. Afterward, the chains are manually corrected if more than two annotators consider it unreasonable.

**判定**: ___　　**理由**: ___

### Has_Longitudinal_Eval
**定义**: 是否包含纵向/长期评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: With Qwen2.5-7B-Instruct as the backbone LLM, we compare the performance of AnnaAgent and baseline methods on anthropomorphism when talking to different counselor models. ... we compare the performance of AnnaAgent and baseline methods on anthropomorphism when talking to different counselor models. ... The results are shown in Table 2.
**cxt 补充证据**: “Multi-session memory challenge … We model multi-session memory as a tertiary memory mechanism. … long-term memory refers to experiences from much earlier times, including the scales and conversations of previous sessions.”

**判定**: ___　　**理由**: ___

### Interaction_Level
**定义**: 交互层级: Single-turn / Short Multi-turn（2-5轮）/ Extended Dialogue（6+轮）/ Longitudinal（跨会话）

| cxt | hyh |
|-----|-----|
| LONGITUDINAL | EXTENDED DIALOGUE |

**eval_report 证据**: Additionally, we use the records in the D4 dataset (Yao et al., 2022) and the DAIC-WOZ dataset (Gratch et al., 2014) as the basis for the previous sessions. ... Specifically, we designed a series of questions similar to those used for personality fidelity to verify the effectiveness of long-term memory by analyzing the answers of virtual seekers.
**cxt 补充证据**: As shown in Figure 3, the content up to and including the last session is defined as long-term memory, that before the start of the current session is real-time memory, and the content in between is defined as short-term memory

**判定**: ___　　**理由**: ___

### Safety
**定义**: 是否避免有害/偏见输出（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The main purpose of this paper is to simulate the seeker more realistically. Thus, we quantitatively compare the performance of different methods in seeker simulation by evaluating the behavioral consistency between simulators and real seekers from different perspectives. ... Anthropomorphism ... Personality Fidelity ... we designed a series of questions similar to those used for personality fidel
**cxt 补充证据**: We organized an Ethical Review Committee consisting of counselors with extensive experience … to avoid other potential ethical risks.”We will only open-source the synthesized sessions’ conversations and the processing code … We will not unconditionally open-source the use of data derived directly from D^4.”

**判定**: ___　　**理由**: ___

### Utility
**定义**: 对任务是否有用/有效（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The main purpose of this paper is to simulate the seeker more realistically. Thus, we quantitatively compare the performance of different methods in seeker simulation by evaluating the behavioral consistency between simulators and real seekers from different perspectives. ... Anthropomorphism ... Personality Fidelity ... we designed a series of questions similar to those used for personality fidel
**cxt 补充证据**: This reseThis research provides innovative solutions to alleviate the global shortage of mental health resources.”arch provides innovative solutions to alleviate the global shortage of mental health resources.”By simulating more realistic seeker behavior, AnnaAgent opens up new paths for psychological research and counselor training.”

**判定**: ___　　**理由**: ___

---
## Paper 21　（4 个分歧）

### Coding Options
**定义**: 是否明确报告了评估者之间的一致性: Yes / No / N/A

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The average consistency between the human experts and GPT-4o reaches 0.72.
**cxt 补充证据**: The average consistency between the human experts and GPT-4o reaches 0.72.

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| EXPERT PRINCIPLES/BEHAVIORAL MODEL | EXPERT PRINCIPLES |

**eval_report 证据**: Inspired by principle-based patient simulation (Louie et al. 2024), we formulate a set of personalized, expert-guided principles for each simulated client. ... Each client profile contains an average of 5 guiding principles, with a maximum of 22, which provide sufficient guidance for the simulation.

**判定**: ___　　**理由**: ___

### Prompt_Disclosure
**定义**: 提示词披露度: Full（清晰提供了所有必要提示词，原则上可复现）/ Partial（展示了部分提示词，不足以复现）/ No（没有可用的提示词信息）

| cxt | hyh |
|-----|-----|
| FULL | PARTIAL |

**eval_report 证据**: the prompts are detailed in the appendix. ... The prompts are detailed in the appendix. ... the specific prompt as follows: ... prompts used are as follows. ... 1) Prompt for Generating Original Responses
**cxt 补充证据**: "附录中完整披露了多个提示词模板，包括

**判定**: ___　　**理由**: ___

### Reliability_Reported
**定义**: 是否报告了标准化评估者间信度系数（如 Cohen's kappa, ICC）: Yes / No / N/A。注意：仅报告百分比一致不算

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The average consistency between the human experts and GPT-4o reaches 0.72.
**cxt 补充证据**: The average consistency between the human experts and GPT-4o reaches 0.72.

**判定**: ___　　**理由**: ___

---
## Paper 23　（4 个分歧）

### Eval_Human_Experts
**定义**: 领域专家（治疗师、临床医生、受过训练的标注员）进行评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: In this section, we evaluate and present the performance of the counseling skill classification approaches proposed in Section IV, including both in-context learning and BERT-based methods.
**cxt 补充证据**: social work experts also verified and discussed the annotations with the annotators.”These weights are determined based on the relevance of each skill to each stage in the MI framework, and are compiled by our social work expert (5-th author).”

**判定**: ___　　**理由**: ___

### Eval_LLM_Judge
**定义**: 使用大模型进行打分、比较、排序（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: In this section, we evaluate and present the performance of the counseling skill classification approaches proposed in Section IV, including both in-context learning and BERT-based methods.
**cxt 补充证据**: The MI controller employs an LLM to evaluate whether the goals of the current MI stage have been achieved.”

**判定**: ___　　**理由**: ___

### Interaction_Level
**定义**: 交互层级: Single-turn / Short Multi-turn（2-5轮）/ Extended Dialogue（6+轮）/ Longitudinal（跨会话）

| cxt | hyh |
|-----|-----|
| EXTENDED DIALOGUE | SINGLE-TURN |

**eval_report 证据**: From the transcript corpus described in Section IV, we collect 4,734 utterance pairs (ci, si) to form our experiment dataset.
**cxt 补充证据**: These dynamic fields are generated before the output message is generated. … having dynamic fields that are updated by the LLM after each message is sent allows for more adaptive behavior.

**判定**: ___　　**理由**: ___

### Utility
**定义**: 对任务是否有用/有效（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: In this section, we evaluate and present the performance of the counseling skill classification approaches proposed in Section IV, including both in-context learning and BERT-based methods.
**cxt 补充证据**: AI-simulated clients can provide students with consistent exposure to a diverse range of client scenarios … A digital system is low cost and hence offer an on-demand solution.”

**判定**: ___　　**理由**: ___

---
## Paper 29　（3 个分歧）

### Comparable_To_Prior_Work
**定义**: 评估是否可与先前研究进行对比（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: We introduce the Counseling Bench, a framework for assessing the effectiveness of the counseling process from seven different perspectives

**判定**: ___　　**理由**: ___

### Eval_Automatic
**定义**: 算法/数学公式自动计算的指标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Leveraging GPT-4 and meticulously crafted prompts based on seven metrics of psychological counseling assessment, the model underwent evaluation using a set of real-world counseling questions.
**cxt 补充证据**: As depicted in Fig.7, ChatCounselor exhibits exceptional performance compared to LLaMA-7B, Alpaca-7B, ChatGLM-v2-7B, and Robins-v2-7B.

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| SURFACE PERSONA | EXPERT PRINCIPLES |

**eval_report 证据**: To incorporate domain knowledge, we employ instruction tuning combined with autoregressive training. When constructing the dataset, our objective is to ensure that responses are not only informative and professional but also incorporate counseling skills such as reflection, active listening, and interaction. Additionally, we strive to capture the natural tone and demeanor of a counseling professio
**cxt 补充证据**: “At the tuning stage, assuming the text input as a sequence of tokens… the training objective is to minimize the auto-regressive loss.”

**判定**: ___　　**理由**: ___

---
## Paper 31　（3 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| STATIC | DYNAMIC |

**eval_report 证据**: Our assessment focuses on the frequency of behavior, the temporal order in which it's expressed, and its adaptability to different client behaviors.

**判定**: ___　　**理由**: ___

### Safety
**定义**: 是否避免有害/偏见输出（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Readiness assessments further need to consider patient safety, which is outside the scope of this study.

**判定**: ___　　**理由**: ___

### Utility
**定义**: 对任务是否有用/有效（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Our evaluation is based on high-quality therapy behaviors and does not incorporate patient outcomes in its assessment, which are challenging to obtain and difficult to simulate.

**判定**: ___　　**理由**: ___

---
## Paper 34　（1 个分歧）

### Prompt_Disclosure
**定义**: 提示词披露度: Full（清晰提供了所有必要提示词，原则上可复现）/ Partial（展示了部分提示词，不足以复现）/ No（没有可用的提示词信息）

| cxt | hyh |
|-----|-----|
| FULL | PARTIAL |

**eval_report 证据**: Example prompts are illustrated in Figure 5 in Appendix C. ... The prompt comprises four key components: the definition of evaluation task, the counseling conversation to be evaluated, the evaluation question and corresponding guidelines.

**判定**: ___　　**理由**: ___

---
## Paper 38　（2 个分歧）

### Prompt_Disclosure
**定义**: 提示词披露度: Full（清晰提供了所有必要提示词，原则上可复现）/ Partial（展示了部分提示词，不足以复现）/ No（没有可用的提示词信息）

| cxt | hyh |
|-----|-----|
| FULL | PARTIAL |

**eval_report 证据**: For client simulation, the prompt used is displayed in Figure 6.

**判定**: ___　　**理由**: ___

### Uses_Dynamic_State
**定义**: 是否使用动态状态建模（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The psychological profile provided to LLMs should significantly influence the counseling session and facilitate the identification of the specific client. Inspired by Schneider et al. (2000) and Chen et al. (2023), we consider the following information: (1) Problems & Reasons for Visiting. ... (2) Displayed Symptoms. ... (3) Apparent Traits. ... Each trait can be described at a severe level. There
**cxt 补充证据**: "We account for the big five personality traits, emotion fluctuations (EF), unwillingness to express emotions (UWE), and resistance toward the therapist (RT).”

**判定**: ___　　**理由**: ___

---
## Paper 47　（4 个分歧）

### Eval_Automatic
**定义**: 算法/数学公式自动计算的指标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we adopt an LLM-as-Judge approach that conducts in-context evaluation using expert-defined reasoning chains grounded in psychological intervention principles. To ensure interpretability, we design expert chain-of-thought reasoning and apply binary point-wise scoring across multiple safety dimensions

**判定**: ___　　**理由**: ___

### Fidelity
**定义**: 是否符合预设角色/目标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We design expert chain-of-thought reasoning and apply binary point-wise scoring across multiple safety dimensions

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| EXPERT PRINCIPLES | SURFACE PERSONA |

**eval_report 证据**: The inputs (x) are drawn from real-world social media posts expressing psychological crisis or risk.

**判定**: ___　　**理由**: ___

### Utility
**定义**: 对任务是否有用/有效（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: D = {dk}5 k=1, f : X × Y →{0, 1}5 ... d1 Empathy and relational stance ... d2 Evidence-based emotional regulation strategies ... d3 Exploration of client concerns ... d4 Risk assessment and identification ... d5 Referral to external resources

**判定**: ___　　**理由**: ___

---
## Paper 49　（1 个分歧）

### Coding Options
**定义**: 是否明确报告了评估者之间的一致性: Yes / No / N/A

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Three professional counselors consistently rate this scale as 7. ... Three experts agree with the given label.

**判定**: ___　　**理由**: ___

---
## Paper 56　（2 个分歧）

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| SURFACE PERSONA | EXPERT PRINCIPLES |

**eval_report 证据**: To elicit answers from a large language model M given Q, we use the following prompting strategies: • Zero-shot (ZS): M answers Qh without task-specific training, using the prompt template in Appendix Table A5. • Few-shot (FS): M answers Qh after seeing demonstrative questions Q1, ..., Qn (Brown, 2020), using the prompt template in Appendix Table A6. We use n = 3 random demonstrative examples. • C

**判定**: ___　　**理由**: ___

### Reliability_Reported
**定义**: 是否报告了标准化评估者间信度系数（如 Cohen's kappa, ICC）: Yes / No / N/A。注意：仅报告百分比一致不算

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: This yielded 845 questions where the 2 annotators were in agreement about the competency annotation and 767 questions where they were in disagreement.

**判定**: ___　　**理由**: ___

---
## Paper 58　（6 个分歧）

### Coding Options
**定义**: 是否明确报告了评估者之间的一致性: Yes / No / N/A

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: ended up with an average accuracy of 90.7% with an agreement rate over 80%

**判定**: ___　　**理由**: ___

### Comparable_To_Prior_Work
**定义**: 评估是否可与先前研究进行对比（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: To assess human performance, we employed another two CBT experts to solve the test set and ended up with an average accuracy of 90.7% with an agreement rate over 80%.

**判定**: ___　　**理由**: ___

### Fidelity
**定义**: 是否符合预设角色/目标（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: Criteria 1: Suggest CBT-consistent goals and tasks that align with an individualized CBT case formulation ... Criteria 4: Maintain consistency with a broad CBT orientation

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: In this paper, we aim to thoroughly examine the potential of using Large Language Models (LLMs) to assist professional psychotherapy. To this end, we propose a new benchmark, CBT-BENCH, for the systematic evaluation of cognitive behavioral therapy (CBT) assistance.

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| EXPERT PRINCIPLES | SURFACE PERSONA |

**eval_report 证据**: Now, you are a professional therapist using cognitive-behavioral therapy (CBT) in a session with a client.

**判定**: ___　　**理由**: ___

### Reliability_Reported
**定义**: 是否报告了标准化评估者间信度系数（如 Cohen's kappa, ICC）: Yes / No / N/A。注意：仅报告百分比一致不算

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: ended up with an average accuracy of 90.7% with an agreement rate over 80%

**判定**: ___　　**理由**: ___

---
## Paper 60　（2 个分歧）

### Eval_Lay_Users
**定义**: 非专家/普通用户进行评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The completed dialogues are then evaluated by experts based on the aforementioned criteria, using a 5-point Likert scale.

**判定**: ___　　**理由**: ___

### Human Learning / Outcomes
**定义**: 是否带来人类进步/改变（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: limitations for training chatbots, leading to a [AUTO-FIXED]

**判定**: ___　　**理由**: ___

---
## Paper 63　（4 个分歧）

### Has_Rubric
**定义**: 是否提供了明确的评分标准/评分指引（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The participants assessed the appropriateness of each response using a 5-point Likert scale, with the labels 'Least appropriate,' 'Inappropriate,' 'Neutral,' 'Appropriate,' and 'Most appropriate.'

**判定**: ___　　**理由**: ___

### Interaction_Level
**定义**: 交互层级: Single-turn / Short Multi-turn（2-5轮）/ Extended Dialogue（6+轮）/ Longitudinal（跨会话）

| cxt | hyh |
|-----|-----|
| SHORT MULTI-TURN | EXTENDED DIALOGUE |

**eval_report 证据**: Each dialogue consisted of approximately 5–10 utterances exchanged between therapist and patient, always concluding with a patient message.

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| SURFACE PERSONA | EXPERT PRINCIPLES |

**eval_report 证据**: a prompt was crafted for the LLMs for generation of a response. This prompt was iteratively refined to align with therapists' conversational style, ensuring responses were open-ended, concise, and therapeutic.

**判定**: ___　　**理由**: ___

### Safety
**定义**: 是否避免有害/偏见输出（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The participants assessed the appropriateness of each response using a 5-point Likert scale, with the labels 'Least appropriate,' 'Inappropriate,' 'Neutral,' 'Appropriate,' and 'Most appropriate.'

**判定**: ___　　**理由**: ___

---
## Paper 65　（3 个分歧）

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| SURFACE PERSONA/DYNAMIC TRAITS | DYNAMIC TRAITS |

**eval_report 证据**: The personality profiles were based on the results from a text classification model fine-tuned for the Big Five Personality Traits[2] with a classification accuracy of 96%.

**判定**: ___　　**理由**: ___

### Prompt_Disclosure
**定义**: 提示词披露度: Full（清晰提供了所有必要提示词，原则上可复现）/ Partial（展示了部分提示词，不足以复现）/ No（没有可用的提示词信息）

| cxt | hyh |
|-----|-----|
| PARTIAL | NO |

**eval_report 证据**: We self-hosted an open-source LLM which made use of accumulated personality information through prompt engineering.

**判定**: ___　　**理由**: ___

### Theory_Operationalized
**定义**: 理论操作化程度: Strong（评估标准明确源于理论）/ Partial（理论被提及并部分操作化）/ Mentioned（理论仅被提及，未操作化）/ None（没有使用任何理论）

| cxt | hyh |
|-----|-----|
| PARTIAL | MENTIONED |

**eval_report 证据**: The personality profiles were based on the results from a text classification model fine-tuned for the Big Five Personality Traits[2] with a classification accuracy of 96%.

**判定**: ___　　**理由**: ___

---
## Paper 68　（4 个分歧）

### Eval_Automatic
**定义**: 算法/数学公式自动计算的指标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: To address this gap, we devised seven metrics (shown in Table 2) for evaluating mental health LLMs. These novel metrics aim to provide a comprehensive evaluation framework that better aligns with the unique requirements of mental health counseling applications.

**判定**: ___　　**理由**: ___

### Has_Failure_Analysis
**定义**: 是否分析了失败案例（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: First, the reliance on synthetic data generated by GPT-3.5 Turbo may introduce biases or lack the depth of real human interactions. Table 3 showed that combining synthetic and interview data during fine-tuning did not consistently improve model performance; in some cases, it led to performance degradation.

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| EXPERT PRINCIPLES/SURFACE PERSONA | EXPERT PRINCIPLES |

**eval_report 证据**: advance research on empathetic, personalized AI solutions to im- [AUTO-FIXED]

**判定**: ___　　**理由**: ___

### Prompt_Disclosure
**定义**: 提示词披露度: Full（清晰提供了所有必要提示词，原则上可复现）/ Partial（展示了部分提示词，不足以复现）/ No（没有可用的提示词信息）

| cxt | hyh |
|-----|-----|
| FULL | NO |

**eval_report 证据**: In addition to the questions, the models were given explicit instructions as follows.

**判定**: ___　　**理由**: ___

---
## Paper 69　（6 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| STATIC | PATTERN-LEVEL |

**eval_report 证据**: Overall, users sent a median of 10.0 messages per conversation (IQR = 8.0−14.0). The median task completion time was 9.2 minutes (IQR = 6.4 − 10.7). ... To estimate user engagement in a conversation, we also analyzed the number of user messages, characters per message (CPM), and words per message (WPM).

**判定**: ___　　**理由**: ___

### Dataset_Available
**定义**: 数据集是否公开可用（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Overall, users sent a median of 10.0 messages per conversation (IQR = 8.0−14.0). The median task completion time was 9.2 minutes (IQR = 6.4 − 10.7).

**判定**: ___　　**理由**: ___

### Has_Failure_Analysis
**定义**: 是否分析了失败案例（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Overall, users sent a median of 10.0 messages per conversation (IQR = 8.0−14.0). The median task completion time was 9.2 minutes (IQR = 6.4 − 10.7).

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we applied the Perceived Empathy of Technology Scale (PETS) [69] to test the following hypotheses: H1a Displaying the agent's internal empathic resonance increases the overall perceived empathy.

**判定**: ___　　**理由**: ___

### Interaction_Level
**定义**: 交互层级: Single-turn / Short Multi-turn（2-5轮）/ Extended Dialogue（6+轮）/ Longitudinal（跨会话）

| cxt | hyh |
|-----|-----|
| SHORT MULTI-TURN | EXTENDED DIALOGUE |

**eval_report 证据**: Overall, users sent a median of 10.0 messages per conversation (IQR = 8.0−14.0).

**判定**: ___　　**理由**: ___

### Theory_Grounding
**定义**: 理论支撑度: Strong（明确使用公认理论来定义或测量）/ Weak（提及了概念但未在评估中实际操作化）/ None（没有真正的理论支撑）

| cxt | hyh |
|-----|-----|
| STRONG | WEAK |

**eval_report 证据**: we applied the Perceived Empathy of Technology Scale (PETS) [69] to test the following hypotheses: H1a Displaying the agent's internal empathic resonance increases the overall perceived empathy.

**判定**: ___　　**理由**: ___

---
## Paper 71　（8 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| STATIC | PATTERN-LEVEL |

**eval_report 证据**: LIWC were calculated per conversation, then averaged over both conversation tasks for each user (N=200 in total, n=50 per group) and analyzed with Kruskal-Wallis tests.

**判定**: ___　　**理由**: ___

### Dataset_Available
**定义**: 数据集是否公开可用（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: A file containing the original FER2013 image names is included in the Supplementary Material. ... The source code is available on https://github.com/kaiaka/mllm-chatbot.git.

**判定**: ___　　**理由**: ___

### Emotional Plausibility
**定义**: 情绪反应是否真实/恰当（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: To assess perceived empathy, we applied the ten PETS items as recommended, as 101-point interactive sliders from strongly disagree to strongly agree in randomized order [92].

**判定**: ___　　**理由**: ___

### Interaction_Level
**定义**: 交互层级: Single-turn / Short Multi-turn（2-5轮）/ Extended Dialogue（6+轮）/ Longitudinal（跨会话）

| cxt | hyh |
|-----|-----|
| SHORT MULTI-TURN | EXTENDED DIALOGUE |

**eval_report 证据**: Your task is to engage in a 5-10 minutes conversation (in English) with our AI assistant about a challenging interpersonal situation you've experienced

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| EXPERT PRINCIPLES | SURFACE PERSONA |

**eval_report 证据**: Your role is to act as an empathic and reflective chatbot, helping users explore and understand a challenging interpersonal situation. Follow these guidelines: - Reflect and respond to the emotions expressed in messages. - Track emotional shifts over time and use this information to guide the conversation and assess progress. - Include short emotional reactions ... - Keep responses concise (2-3 se

**判定**: ___　　**理由**: ___

### Safety
**定义**: 是否避免有害/偏见输出（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: To assess perceived empathy, we applied the ten PETS items as recommended, as 101-point interactive sliders from strongly disagree to strongly agree in randomized order [92].

**判定**: ___　　**理由**: ___

### Theory_Operationalized
**定义**: 理论操作化程度: Strong（评估标准明确源于理论）/ Partial（理论被提及并部分操作化）/ Mentioned（理论仅被提及，未操作化）/ None（没有使用任何理论）

| cxt | hyh |
|-----|-----|
| PARTIAL | STRONG |

**eval_report 证据**: Empathy can be seen as a dimensional construct consisting of a cognitive and an affective component [11, 25, 28, 92].

**判定**: ___　　**理由**: ___

### Uses_Dynamic_State
**定义**: 是否使用动态状态建模（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The system captured the webcam's RGB video stream at 5 fps and cropped it to the detected face bounding box ... The captured images were buffered with a resolution of 120x160 pixels and continuously added to a single buffer grid image that depicted the images of the last four seconds. This grid image was initially filled from the top left and shifted correspondingly on every new incoming image. ..

**判定**: ___　　**理由**: ___

---
## Paper 72　（3 个分歧）

### Eval_Human_Experts
**定义**: 领域专家（治疗师、临床医生、受过训练的标注员）进行评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: No real client transcripts or clinician interactions were used; ecological validity must be confirmed with human subjects.

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The experimental evaluation benchmarks the proposed framework using four prevailing LLMs: Llama-4-scout-17b, Mistral-Saba-24b, Qwen-QWQ-32b and OpenAI GPT-4.1-Nano. ... Simulated client profiles cover 10 primary mental disorder categories: (1) Adjustment Disorder, (2) Anxiety, (3) Bipolar Disorder, (4) Depression, (5) Obsessive–Compulsive Disorder (OCD), (6) Panic Disorder, (7) Post-Traumatic Stre

**判定**: ___　　**理由**: ___

### LLM_Judge_Validated
**定义**: LLM裁判是否经过验证（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Automatic evaluation bias. Rubric scoring relied on another LLM, which could share error modes or biases with the models under test. ... Further validation, including expert human review and targeted assessment of diagnostic rationale quality, is needed.

**判定**: ___　　**理由**: ___

---
## Paper 75　（5 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| DYNAMIC | PATTERN-LEVEL |

**eval_report 证据**: For each transcript, we computed the proportion of utterances showing strong skill use (� = �strengths/�total) or needing improvement (� = �improvement/�total) ... To test for pre-post changes (�0, �1), we used paired � -tests and Cohen's � effect sizes. To compare P and P+F groups (�� 1 − �� 0 vs. ��� 1 − �� � 0 ), we used unpaired � -tests

**判定**: ___　　**理由**: ___

### Emotional Plausibility
**定义**: 情绪反应是否真实/恰当（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: We measured participants’ perceptions of each of the AI patients after each chat (pre-intervention, practice intervention, post-intervention) with several 7-point Likert scale items. Authenticity. Participants rated “The AI patient was authentic in its role.”

**判定**: ___　　**理由**: ___

### Eval_LLM_Judge
**定义**: 使用大模型进行打分、比较、排序（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: We developed LLM-based binary classifiers to label skill use within transcripts. For example, one classifier determines which utterances showed strong use of Questions. To finetune and evaluate these classifiers, we transformed a previously published expert-annotated feedback dataset [18] into 16-class binary classification format ... We finetuned RoBERTa-large binary classifiers using FeedbackQES

**判定**: ___　　**理由**: ___

### Reliability_Reported
**定义**: 是否报告了标准化评估者间信度系数（如 Cohen's kappa, ICC）: Yes / No / N/A。注意：仅报告百分比一致不算

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: While we initially explored metrics like Cohen’s kappa, severe class imbalance made them less relevant.

**判定**: ___　　**理由**: ___

### Uses_Dynamic_State
**定义**: 是否使用动态状态建模（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: the patient simulation did not adapt its behaviors to empathic statements ... the simulated patient was instructed to resist suggestions, so counselors reduced their uses of suggestions, while the patient simulation did not adapt its behaviors to empathic statements ... A natural follow-up question concerns whether patient simulations that adapt to counselor behavior promote better skill acquisiti

**判定**: ___　　**理由**: ___

---
## Paper 77　（5 个分歧）

### Coding Options
**定义**: 是否明确报告了评估者之间的一致性: Yes / No / N/A

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: participants rated on a Likert scale from 1 to 5, where 1 is strongly disagree and 5 is strongly agree.

**判定**: ___　　**理由**: ___

### Has_Failure_Analysis
**定义**: 是否分析了失败案例（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: participants rated on a Likert scale from 1 to 5, where 1 is strongly disagree and 5 is strongly agree.

**判定**: ___　　**理由**: ___

### Interaction_Level
**定义**: 交互层级: Single-turn / Short Multi-turn（2-5轮）/ Extended Dialogue（6+轮）/ Longitudinal（跨会话）

| cxt | hyh |
|-----|-----|
| SHORT MULTI-TURN | EXTENDED DIALOGUE |

**eval_report 证据**: another limitation of the present study was the abridged nature of the transcripts (approximately 5 minutes duration) and their restricted focus on active listening during problem exploration.

**判定**: ___　　**理由**: ___

### Theory_Grounding
**定义**: 理论支撑度: Strong（明确使用公认理论来定义或测量）/ Weak（提及了概念但未在评估中实际操作化）/ None（没有真正的理论支撑）

| cxt | hyh |
|-----|-----|
| STRONG | WEAK |

**eval_report 证据**: We selected four therapy transcripts from three different books on CBT to use as our basis (Beck, 2011; Ellis, 1995; Sommers-Flanagan & Sommers-Flanagan, 2018). ... To evaluate communication skills, we used the questions "The therapist communicated clearly and accurately" and "The therapist demonstrated accurate reflection of client's expressed feelings, avoiding under or overshooting," which were

**判定**: ___　　**理由**: ___

### Theory_Operationalized
**定义**: 理论操作化程度: Strong（评估标准明确源于理论）/ Partial（理论被提及并部分操作化）/ Mentioned（理论仅被提及，未操作化）/ None（没有使用任何理论）

| cxt | hyh |
|-----|-----|
| PARTIAL | MENTIONED |

**eval_report 证据**: Among the various therapeutic approaches, Cognitive Behavioral Therapy (CBT) stands out as a crucial element in the design of these chatbots (Rathnayaka et al., 2022). ... We selected four therapy transcripts from three different books on CBT to use as our basis (Beck, 2011; Ellis, 1995; Sommers-Flanagan & Sommers-Flanagan, 2018).

**判定**: ___　　**理由**: ___

---
## Paper 80　（4 个分歧）

### Emotional Plausibility
**定义**: 情绪反应是否真实/恰当（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We evaluate the AI patients created by counselors on criteria inspired by prior work evaluating Standardized Patients, who are trained human actors, on their ability to roleplay a case (Himmelbauer et al., 2018). ... Counselors rated the two AI patients based on 6 dimensions (Table 3).

**判定**: ___　　**理由**: ___

### Safety
**定义**: 是否避免有害/偏见输出（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we develop Roleplay-doh, a novel human-LLM collaboration pipeline that elicits qualitative feedback from a domain-expert, which is transformed into a set of principles, or natural language rules, that govern an LLM-prompted roleplay. ... It is impossible to promise that all interactions with an LLM such as GPT-4 result in satisfactory responses. Therefore, meaningless, derogatory, and otherwise ha

**判定**: ___　　**理由**: ___

### Uses_Dynamic_State
**定义**: 是否使用动态状态建模（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: experts customize a set of principles, or rules written in natural language that govern its behavior ... We prompt GPT-4 conditioned on patient description, list of principles and conversation history to generate an initial patient response at each conversation turn.

**判定**: ___　　**理由**: ___

### Uses_Standard_Metrics
**定义**: 是否使用了标准/公认的评估指标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We evaluate the AI patients created by counselors on criteria inspired by prior work evaluating Standardized Patients, who are trained human actors, on their ability to roleplay a case (Himmelbauer et al., 2018).

**判定**: ___　　**理由**: ___

---
## Paper 81　（4 个分歧）

### Has_Failure_Analysis
**定义**: 是否分析了失败案例（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: our measures of the training effectiveness are all perceived improvements from the participants after they practice with PATIENT-Ψ-TRAINER for two sessions. Measuring objective skill improvements could take the form of longitudinal randomized controlled trials (RCTs).

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: In this work, we evaluate our framework using GPT-4. As we do not rely on specific properties of GPT-4, we believe the framework could be applied to any powerful open-source LLMs such as Llama 3 (Dubey et al., 2024) and Gemma (Team et al., 2024). ... our measures of the training effectiveness are all perceived improvements from the participants after they practice with PATIENT-Ψ-TRAINER for two se

**判定**: ___　　**理由**: ___

### Has_Rubric
**定义**: 是否提供了明确的评分标准/评分指引（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: Individual measures use a 5-point Likert scale from 1 to 5, where 5 means “strongly agree” or “extremely accurate,” and 1 means “strongly disagree” or “not accurate at all.” ... For pairwise comparisons, the options are: “A is much better than B,” “A is somewhat better than B,” “about the same,” “B is somewhat better than A,” and “B is much better than A.” We map the results to a scale from -2 to 

**判定**: ___　　**理由**: ___

### Interaction_Level
**定义**: 交互层级: Single-turn / Short Multi-turn（2-5轮）/ Extended Dialogue（6+轮）/ Longitudinal（跨会话）

| cxt | hyh |
|-----|-----|
| EXTENDED DIALOGUE | SHORT MULTI-TURN |

**eval_report 证据**: Each session of interacting with a simulated patient took around 10 minutes, inclusive of chatting with the LLM and completing the cognitive model.

**判定**: ___　　**理由**: ___

---
## Paper 83　（7 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| DYNAMIC | STATIC |

**eval_report 证据**: Finally, we modify the Positive and Negative Affect Schedule (PANAS) (Watson et al., 1988) to assess the effectiveness of counseling from the client's perspective, measuring changes in the client's positive/negative emotions before/after counseling sessions. ... we leverage intake forms to infer the client's emotional state before counseling and predict changes in their emotional state after recei

**判定**: ___　　**理由**: ___

### Coding Options
**定义**: 是否明确报告了评估者之间的一致性: Yes / No / N/A

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: For each evaluation, we asked three human annotators to assess 100 samples based on four specified criteria. We compensated each annotator $0.30 per evaluated sample.

**判定**: ___　　**理由**: ___

### Emotional Plausibility
**定义**: 情绪反应是否真实/恰当（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We randomly sample 100 dialogues from each dataset and evaluate them according to four criteria: (1) Helpfulness, (2) Coherence, (3) Empathy, and (4) Guidance. ... The metrics to assess general counseling skills are as follows: Understanding, Interpersonal Effectiveness, Collaboration ... the metrics to assess CBT-specific skills are as follows: Guided Discovery, Focus, Strategy

**判定**: ___　　**理由**: ___

### Eval_Automatic
**定义**: 算法/数学公式自动计算的指标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: For evaluation, we use G-Eval (Liu et al., 2023b) to assess each criterion in the Likert-scale with a scoring rubric. ... CTRS, recognized as the gold standard for measuring counseling effectiveness (Aarons et al., 2012). ... we modify the Positive and Negative Affect Schedule (PANAS) (Watson et al., 1988) to assess the effectiveness of counseling from the client's perspective

**判定**: ___　　**理由**: ___

### Fidelity
**定义**: 是否符合预设角色/目标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We randomly sample 100 dialogues from each dataset and evaluate them according to four criteria: (1) Helpfulness, (2) Coherence, (3) Empathy, and (4) Guidance.

**判定**: ___　　**理由**: ___

### Has_Failure_Analysis
**定义**: 是否分析了失败案例（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: AI counselors have limitations in selecting CBT techniques ... GPT-4o exhibits a biased selection of CBT techniques, with Evidence-Based Questioning being utilized in almost half of all cases ... AI counselors tend to suggest direct reframing of the clients' thoughts ... AI clients tend to express the provided information explicitly ... AI clients tend to be overly positive ... CAMEL-LLAMA3 shows 

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we introduce CACTUS, a multi-turn dialogue dataset that emulates real-life interactions using the goal-oriented and structured approach of Cognitive Behavioral Therapy (CBT) ... We create a diverse and realistic dataset by (1) designing clients with varied, specific personas, and (2) having counselors systematically apply CBT techniques in their interactions.

**判定**: ___　　**理由**: ___

---
## Paper 84　（10 个分歧）

### Coding Options
**定义**: 是否明确报告了评估者之间的一致性: Yes / No / N/A

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Each conversation context was evaluated by at least 3 participants. Presenting models in a fixed sequence can compromise reliability by introducing potential order effects (van der Lee et al., 2021). To minimize this, we applied Balanced Latin Square counterbalancing where each model appears equally often in every position.

**判定**: ___　　**理由**: ___

### Consistency
**定义**: 跨轮次行为是否稳定（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We evaluated single chatbot reflections generated based on a context of 5 preceding turns. Longer context or an integration of a conversation memory could give us a much better indication to what extent LLMs can add variation to make the counseling sessions more engaging so that users are willing to participate in long-term interactions.

**判定**: ___　　**理由**: ___

### Dataset_Available
**定义**: 数据集是否公开可用（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The data are not publicly distributed at this time.

**判定**: ___　　**理由**: ___

### Eval_Human_Experts
**定义**: 领域专家（治疗师、临床医生、受过训练的标注员）进行评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Following a previous study showing that non-experts can provide reflection evaluations as reliable as MI experts (Wu et al., 2023), we employed non-experts as participants of our evaluation study.

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: We use GPT-4, BLOOM, and FLAN-T5 models to generate motivational interviewing reflections, based on real conversational data collected via chatbots designed to provide support for smoking cessation and sexual health.

**判定**: ___　　**理由**: ___

### Reliability_Reported
**定义**: 是否报告了标准化评估者间信度系数（如 Cohen's kappa, ICC）: Yes / No / N/A。注意：仅报告百分比一致不算

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: A one-way ANOVA revealed the significance of the effect for all four criteria (appropriateness: F(3, 184) = 29.956, p < 0.001; specificity: F(3, 184) = 46.02, p < 0.001; naturalness: F(3, 184) = 14.874, p < 0.001; engagement: F(3, 184) = 29.926, p < 0.001). Tukey's HSD post-hoc test for multiple comparisons indicated that GPT-4 reflections were rated significantly higher ... A Kruskal-Wallis test 

**判定**: ___　　**理由**: ___

### Sim_Behavior_Realistic
**定义**: 模拟行为是否真实（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We define the naturalness criterion as whether the response sounds like it could have been uttered by a person. ... BLOOM and FLAN-T5 models often generate repetitive sequences which we automatically shorten to their simplest forms in a post-processing step.

**判定**: ___　　**理由**: ___

### Theory_Grounding
**定义**: 理论支撑度: Strong（明确使用公认理论来定义或测量）/ Weak（提及了概念但未在评估中实际操作化）/ None（没有真正的理论支撑）

| cxt | hyh |
|-----|-----|
| STRONG | WEAK |

**eval_report 证据**: Motivational Interviewing (MI) is a counseling style for eliciting behavior change, where the counselors guide individuals towards evoking their intrinsic motivations by addressing and resolving their ambivalence (Miller and Rollnick, 2012). A crucial technique that MI counselors utilize is reflective listening, where they engage in attentive listening and offer reflections on their clients' persp

**判定**: ___　　**理由**: ___

### Theory_Operationalized
**定义**: 理论操作化程度: Strong（评估标准明确源于理论）/ Partial（理论被提及并部分操作化）/ Mentioned（理论仅被提及，未操作化）/ None（没有使用任何理论）

| cxt | hyh |
|-----|-----|
| STRONG | PARTIAL |

**eval_report 证据**: Counselling studies indicate a direct relationship between engagement and positive therapeutic results and improvements (Boardman et al., 2006).

**判定**: ___　　**理由**: ___

### Uses_Standard_Metrics
**定义**: 是否使用了标准/公认的评估指标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We implement a 7-point symmetric Likert scale ranging from Strongly disagree (−3) to Strongly agree (3) (Amidei et al., 2019).

**判定**: ___　　**理由**: ___

---
## Paper 86　（3 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| STATIC | PATTERN-LEVEL |

**eval_report 证据**: We finally evaluate the KL divergence of action distributions between the simulated clients and real clients for the different methods.

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| BEHAVIORAL STATE MODEL/DYNAMIC TRAITS | BEHAVIORAL STATE MODEL |

**eval_report 证据**: Unlike the previous approaches, our framework explicitly models four aspects of client profiles, i.e., motivation, beliefs, preferred change plans, and receptivity.

**判定**: ___　　**理由**: ___

### Safety
**定义**: 是否避免有害/偏见输出（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We employ four of our co-authors, who are experts in psychology and experienced in MI counseling, as annotators. ... Specifically, we employ GPT-4 to perform entailment assessment in a few-shot manner.

**判定**: ___　　**理由**: ___

---
## Paper 87　（5 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| STATIC | PATTERN-LEVEL |

**eval_report 证据**: We report the following behavior-counts: 1) Reflection Question Ratio (R/Q), defined by the number of reflections by the counselor agent divided by the number of questions asked by the counselor; 2) Proportion of Open Questions (%OQ), defined by the number of open questions asked by counselor divided by the number of questions (including both open and closed questions); 3) Proportion of Complex Re

**判定**: ___　　**理由**: ___

### Emotional Plausibility
**定义**: 情绪反应是否真实/恰当（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: Empathy, which measures the extent to which the counselor attempts to understand the client's perspective and experience, essentially trying to 'try on' what the client feels or thinks.

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: For counselor, we experiment with both gpt-4o-2024-08-06 and Llama-3.1-70B LLM backbones.

**判定**: ___　　**理由**: ___

### Human Learning / Outcomes
**定义**: 是否带来人类进步/改变（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: Successful change talk is the main goal of MI. We therefore introduce success rate defined by the proportion of clients with whom the counselor agent successfully evokes change talk, resulting in increased motivation to change at the end of session.

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| DYNAMIC TRAITS | BEHAVIORAL STATE MODEL |

**eval_report 证据**: To define the client's states (Prochaska and Velicer, 1997; Hashemzadeh et al., 2019), we utilize the transtheoretical model of health behavior change (Prochaska and DiClemente, 2005; Prochaska et al., 2008), which defines five possible states: Precontemplation, Contemplation, Preparation, Action, and Maintenance.

**判定**: ___　　**理由**: ___

---
## Paper 89　（5 个分歧）

### Eval_Lay_Users
**定义**: 非专家/普通用户进行评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Our evaluation team consists of four senior psychological postgraduate students and an experienced psychotherapist to ensure accuracy and professionalism.

**判定**: ___　　**理由**: ___

### Has_Failure_Analysis
**定义**: 是否分析了失败案例（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Our framework only constructs digital twin of psychological counselor with specific counseling style, which satisfies the individual needs of clients who seek specific counseling style, but can not guarantee to solve their psychological problems and meet counseling needs of all clients.

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: To validate that our synthetic multi-turn dialogues dataset, PsyDTCorpus, integrates linguistic style, therapy technique, and client personality, we design three ablation manual evaluations. ... we synthesize these 16 sets of dialogues, each time excluding one of the following elements: linguistic style, therapy technique, and client personality. ... For each topic, we randomly select 20 single-tu

**判定**: ___　　**理由**: ___

### LLM_Judge_Validated
**定义**: LLM裁判是否经过验证（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Given the potential of using LLMs for evaluating text generation quality (Chiang and Lee, 2023), we attempt to automatically assess the similarity ... We employ two state-of-the-art LLMs as evaluators: GPT-4o and Claude 3.5. We take the average of the similarity scores given by two LLMs as the final result.

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| COGNITIVE MODEL/EXPERT PRINCIPLES | SURFACE PERSONA |

**eval_report 证据**: we employ GPT-4 to simulate the Big Five personality traits (Costa and McCrae, 1999) of clients based on their question

**判定**: ___　　**理由**: ___

---
## Paper 91　（3 个分歧）

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Our experiments show significant performance variations across fine-tuning, prompt engineering, and retrieval augmented generation (RAG) approaches. However, this study does not conduct robustness testing under perturbed or adversarial input conditions.

**判定**: ___　　**理由**: ___

### Has_Rubric
**定义**: 是否提供了明确的评分标准/评分指引（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Classification evaluations are performed using F1 score, precision, and recall as our main metrics.

**判定**: ___　　**理由**: ___

### Safety
**定义**: 是否避免有害/偏见输出（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Classification evaluations are performed using F1 score, precision, and recall as our main metrics.

**判定**: ___　　**理由**: ___

---
## Paper 92　（5 个分歧）

### Coding Options
**定义**: 是否明确报告了评估者之间的一致性: Yes / No / N/A

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Each participant evaluated reflections for both independent and ranking evaluations across 3 randomly assigned conversation contexts. Eventually, each context was evaluated by at least 3 different participants.

**判定**: ___　　**理由**: ___

### Reliability_Reported
**定义**: 是否报告了标准化评估者间信度系数（如 Cohen's kappa, ICC）: Yes / No / N/A。注意：仅报告百分比一致不算

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Each participant evaluated reflections for both independent and ranking evaluations across 3 randomly assigned conversation contexts. Eventually, each context was evaluated by at least 3 different participants.

**判定**: ___　　**理由**: ___

### Safety
**定义**: 是否避免有害/偏见输出（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: Appropriateness measures whether the reflection would be (emotionally and morally) appropriate if it is actually uttered to a client after the given conversation.

**判定**: ___　　**理由**: ___

### Theory_Grounding
**定义**: 理论支撑度: Strong（明确使用公认理论来定义或测量）/ Weak（提及了概念但未在评估中实际操作化）/ None（没有真正的理论支撑）

| cxt | hyh |
|-----|-----|
| STRONG | WEAK |

**eval_report 证据**: The criteria are chosen by considering their relevance and importance to therapeutic counseling and their common usage in the NLG field. For instance, we look into appropriateness because inappropriate reflections can hinder the clients’ progress towards their behavior change goals (Miller and Rollnick, 2012). Similarly, clients’ engagement during counseling shown to be closely linked to their the

**判定**: ___　　**理由**: ___

### Utility
**定义**: 对任务是否有用/有效（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: Engagement to see whether the reflection could provide the opportunity for further conversation and could increase the engagement.

**判定**: ___　　**理由**: ___

---
## Paper 93　（5 个分歧）

### Emotional Plausibility
**定义**: 情绪反应是否真实/恰当（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: INT (Interactive Narrative Therapist) simulates expert narrative therapists by planning therapeutic stages, guiding reflection levels, and generating contextually appropriate expert-like responses

**判定**: ___　　**理由**: ___

### Has_Failure_Analysis
**定义**: 是否分析了失败案例（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: INT (Interactive Narrative Therapist) simulates expert narrative therapists by planning therapeutic stages, guiding reflection levels, and generating contextually appropriate expert-like responses

**判定**: ___　　**理由**: ___

### Has_Longitudinal_Eval
**定义**: 是否包含纵向/长期评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: further longitudinal studies are needed to confirm whether narrative transformation markers translate to measurable well-being outcomes

**判定**: ___　　**理由**: ___

### Realism
**定义**: 输出是否像人类或自然（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: INT (Interactive Narrative Therapist) simulates expert narrative therapists by planning therapeutic stages, guiding reflection levels, and generating contextually appropriate expert-like responses

**判定**: ___　　**理由**: ___

### Sim_Behavior_Realistic
**定义**: 模拟行为是否真实（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: INT (Interactive Narrative Therapist) simulates expert narrative therapists by planning therapeutic stages, guiding reflection levels, and generating contextually appropriate expert-like responses

**判定**: ___　　**理由**: ___

---
## Paper 94　（8 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| STATIC | PATTERN-LEVEL |

**eval_report 证据**: Figure 3 illustrates the strategy distributions obtained by various approaches. ... Our proposed MultiAgentESC demonstrates a more balanced and diversified distribution of strategy selection, effectively mitigating the risk of over-reliance on a limited set of strategies. All strategies within MultiAgentESC maintain utilization rates exceeding 3%, with none surpassing one-third of the total usage.

**判定**: ___　　**理由**: ___

### Eval_Lay_Users
**定义**: 非专家/普通用户进行评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we propose a training-free Multi-Agent collaboration framework for ESC (MultiAgentESC). The framework is designed to emulate the human-like process of providing emotional support through three stages: dialogue analysis, strategy deliberation, and response generation.

**判定**: ___　　**理由**: ___

### Eval_User_Study
**定义**: 结构化实验，用户与系统发生交互（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we randomly sample 100 dialogues from the test set of the ESConv dataset and instruct the annotators to assume the role of help-seekers under these dialogue scenarios. Each annotator is tasked with comparing all responses generated by our method against those produced by other methods across the 100 dialogues.

**判定**: ___　　**理由**: ___

### Fidelity
**定义**: 是否符合预设角色/目标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we propose a training-free Multi-Agent collaboration framework for ESC (MultiAgentESC). The framework is designed to emulate the human-like process of providing emotional support through three stages: dialogue analysis, strategy deliberation, and response generation.

**判定**: ___　　**理由**: ___

### Reliability_Reported
**定义**: 是否报告了标准化评估者间信度系数（如 Cohen's kappa, ICC）: Yes / No / N/A。注意：仅报告百分比一致不算

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we recruit three postgraduate students with psychology backgrounds as annotators to evaluate the performance of our proposed MultiAgentESC framework and other methods. ... sign test, ∗represents p-value < 0.05

**判定**: ___　　**理由**: ___

### Safety
**定义**: 是否避免有害/偏见输出（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Without appropriate protective measures, they may generate harmful content. Consequently, our objective is to deliver emotional support within the context of daily dialogue, without replacing professional psychological therapy.

**判定**: ___　　**理由**: ___

### Theory_Grounding
**定义**: 理论支撑度: Strong（明确使用公认理论来定义或测量）/ Weak（提及了概念但未在评估中实际操作化）/ None（没有真正的理论支撑）

| cxt | hyh |
|-----|-----|
| STRONG | WEAK |

**eval_report 证据**: most existing methods tend to generate responses directly, with limited consideration with respect to the social interdependence theory (Johnson, 2003) and the Helping Skills Theory (Hill and O'Brien, 1999), which emphasize domain-specific reasoning and expert cooperation during the process of providing emotional support.

**判定**: ___　　**理由**: ___

### Theory_Operationalized
**定义**: 理论操作化程度: Strong（评估标准明确源于理论）/ Partial（理论被提及并部分操作化）/ Mentioned（理论仅被提及，未操作化）/ None（没有使用任何理论）

| cxt | hyh |
|-----|-----|
| STRONG | MENTIONED |

**eval_report 证据**: most existing methods tend to generate responses directly, with limited consideration with respect to the social interdependence theory (Johnson, 2003) and the Helping Skills Theory (Hill and O'Brien, 1999), which emphasize domain-specific reasoning and expert cooperation during the process of providing emotional support.

**判定**: ___　　**理由**: ___

---
## Paper 95　（7 个分歧）

### Eval_Automatic
**定义**: 算法/数学公式自动计算的指标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Table 2: Therapist skills assessment scores calculated by GPT-4O ... Table 3: Client alliance assessment results as evaluated by GPT-4O.

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| COGNITIVE MODEL / BEHAVIORAL STATE | BEHAVIORAL STATE MODEL |

**eval_report 证据**: We further augment each client profile with four distinct resistance types: cognitive, emotional, behavioral, and non-resistant, following the taxonomy proposed by Beal III et al. (2013). Rather than assigning a single resistance label to each profile, we generate four variants per client, each conditioned on a different resistance type.

**判定**: ___　　**理由**: ___

### Prompt_Disclosure
**定义**: 提示词披露度: Full（清晰提供了所有必要提示词，原则上可复现）/ Partial（展示了部分提示词，不足以复现）/ No（没有可用的提示词信息）

| cxt | hyh |
|-----|-----|
| FULL | NO |

**eval_report 证据**: Therapist skills were assessed using the prompts provided in the official COUNSELINGEVAL code20 by Lee et al. (2024a). ... The detailed evaluation guidelines for each question follow those provided in Li et al. (2024a) and are not reproduced here for brevity.

**判定**: ___　　**理由**: ___

### Realism
**定义**: 输出是否像人类或自然（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: To guide the development and evaluation of such models, we define two key assessment dimensions that reflect essential aspects of effective therapy: • Therapist Skills Assessment: Evaluates the AI therapist's competence in two key categories of general counseling skills and CBT-specific techniques. • Client Alliance Assessment: Focuses on the AI therapist's ability to establish a strong therapeuti

**判定**: ___　　**理由**: ___

### Safety
**定义**: 是否避免有害/偏见输出（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: To guide the development and evaluation of such models, we define two key assessment dimensions that reflect essential aspects of effective therapy: • Therapist Skills Assessment: Evaluates the AI therapist's competence in two key categories of general counseling skills and CBT-specific techniques. • Client Alliance Assessment: Focuses on the AI therapist's ability to establish a strong therapeuti

**判定**: ___　　**理由**: ___

### Sim_Behavior_Realistic
**定义**: 模拟行为是否真实（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: The case analysis demonstrates that MIRRORP+EC effectively identifies the client's emotional state through captioning and responds with emotional validation16 and open-ended questions, common therapeutic techniques for managing resistance (Miller and Rollnick, 2002).

**判定**: ___　　**理由**: ___

### Simulation_Target
**定义**: 模拟的对象: Client Agent / Therapist Agent / Dual-Agent / Human Trainee

| cxt | hyh |
|-----|-----|
| THERAPIST AGENT | CLIENT AGENT |

**eval_report 证据**: We adopt GPT-3.5-TURBO12 as the virtual client and conduct simulations based on predefined multimodal profiles.

**判定**: ___　　**理由**: ___

---
## Paper 97　（1 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| DYNAMIC | PATTERN-LEVEL |

**eval_report 证据**: To analyze the behavior of LLM therapists in the exploration stage, we automatically annotate the strategy per utterance and visualize the distribution of strategies utilized per model.

**判定**: ___　　**理由**: ___

---
## Paper 99　（7 个分歧）

### Coding Options
**定义**: 是否明确报告了评估者之间的一致性: Yes / No / N/A

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Overall, 85.2% of extracted traits were verified as accurate extraction. Among these, 57.6% acknowledge indirect but reasonable inferences made by the model.

**判定**: ___　　**理由**: ___

### Has_Failure_Analysis
**定义**: 是否分析了失败案例（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: First, our human evaluation is conducted using fifteen human experts. Second, we did not perform ablations of the individual contribution of each alignment component to the final model's effectiveness, mainly because of the dilemma we are facing – the human evaluation is costly while the automatic evaluation is not effective enough to uncover subtle differences. Finally, we were unable to fully ex

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: First, our human evaluation is conducted using fifteen human experts. Second, we did not perform ablations of the individual contribution of each alignment component to the final model's effectiveness, mainly because of the dilemma we are facing – the human evaluation is costly while the automatic evaluation is not effective enough to uncover subtle differences. Finally, we were unable to fully ex

**判定**: ___　　**理由**: ___

### LLM_Judge_Validated
**定义**: LLM裁判是否经过验证（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: However, as our findings suggest, automatic evaluation struggles to capture nuanced differences between models, highlighting the indispensable role of expert assessment. ... No significant differences are observed, as the interviewer agent consistently assigns high ratings, failing to capture the subtle differences as could be observed in human evaluation. These findings highlight the limited sens

**判定**: ___　　**理由**: ___

### Prompt_Disclosure
**定义**: 提示词披露度: Full（清晰提供了所有必要提示词，原则上可复现）/ Partial（展示了部分提示词，不足以复现）/ No（没有可用的提示词信息）

| cxt | hyh |
|-----|-----|
| FULL | PARTIAL |

**eval_report 证据**: Eeyore and all annotated data are open-sourced at https://github.com/MichiganNLP/Eeyore. ... Figure 2: Pipeline to input data for instruction-tuning. ... Table 7: Structured questioning framework used by the interviewer agent across three dimensions. ... Appendix B: Training and Inference Details.

**判定**: ___　　**理由**: ___

### Reliability_Reported
**定义**: 是否报告了标准化评估者间信度系数（如 Cohen's kappa, ICC）: Yes / No / N/A。注意：仅报告百分比一致不算

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Despite alignment efforts, the model may still generate inaccuracies, potentially leading to educational errors. Additionally, hallucinations remain a concern, necessitating cautious use in clinical training settings.

**判定**: ___　　**理由**: ___

### Uses_Standard_Metrics
**定义**: 是否使用了标准/公认的评估指标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Evaluators assess the models across five dimensions using a 5-point Likert scale. ... The first four dimensions focus on different facets of authenticity, while the final dimension evaluates profile adherence: Contrast with AI-Like Responses, Linguistic Authenticity, Cognitive Pattern Authenticity, Subtle Emotional Expression, Profile Adherence and Personalization

**判定**: ___　　**理由**: ___

---
## Paper 100　（5 个分歧）

### Consistency
**定义**: 跨轮次行为是否稳定（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: synthetic dialogues are fluent and structurally coherent, they diverge from real conversations in key emotional properties: real sessions exhibit greater emotional variability, more emotion-laden language, and more authentic patterns of reactivity and regulation

**判定**: ___　　**理由**: ___

### Prompt_Disclosure
**定义**: 提示词披露度: Full（清晰提供了所有必要提示词，原则上可复现）/ Partial（展示了部分提示词，不足以复现）/ No（没有可用的提示词信息）

| cxt | hyh |
|-----|-----|
| FULL | NO |

**eval_report 证据**: We employed three state-of-the-art language models (i.e., ChatGPT-4o Mini, Grok-v3, and Gemini 2.0 Flash) to independently infer these tags for each dialogue.

**判定**: ___　　**理由**: ___

### Sim_Behavior_Realistic
**定义**: 模拟行为是否真实（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: synthetic dialogues are fluent and structurally coherent, they diverge from real conversations in key emotional properties: real sessions exhibit greater emotional variability, more emotion-laden language, and more authentic patterns of reactivity and regulation ... These findings underscore the limitations of current LLM-generated therapy data and highlight the importance of emotional fidelity in

**判定**: ___　　**理由**: ___

### Theory_Operationalized
**定义**: 理论操作化程度: Strong（评估标准明确源于理论）/ Partial（理论被提及并部分操作化）/ Mentioned（理论仅被提及，未操作化）/ None（没有使用任何理论）

| cxt | hyh |
|-----|-----|
| STRONG | MENTIONED |

**eval_report 证据**: Table 1 provides representative examples from each, along with interpretive commentary informed by key psychotherapy theories (e.g., emotion regulation (Gross, 1998), calibrated empathy (Elliott et al., 2018, 2013), affective co-regulation (Butler and Randall, 2013), and therapeutic alliance theory (Bordin, 1979)).

**判定**: ___　　**理由**: ___

### Uses_Dynamic_State
**定义**: 是否使用动态状态建模（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we adopt the Utterance Emotion Dynamics (UED) framework to compute emotion metrics from sequences of utterances, treating each role (counselor or client) as a separate character trajectory.

**判定**: ___　　**理由**: ___

---
## Paper 101　（4 个分歧）

### Eval_Automatic
**定义**: 算法/数学公式自动计算的指标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: PersonaScore, a human-aligned automatic metric grounded in decision theory that enables comprehensive large-scale evaluation. ... PersonaScore evaluates these responses using expert-curated rubrics. ... To align PersonaScore with human preferences, we first generate exemplar responses at each rubric level using LLM reasoners, effectively calibrating the evaluators. Multiple state-of-the-art LLM ev

**判定**: ___　　**理由**: ___

### Sim_Behavior_Realistic
**定义**: 模拟行为是否真实（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: To test the alignment of PersonaScore with Human Judgment, we conducted a human study on a subsample of 100 personas across three models (GPT-3.5, LLAMA-2-13B, and LLAMA-2-70B) in our experiments, totaling 1500 model responses. ... PersonaScore is Highly Correlated with Human Judgment Table 3 show strong correlations between Spearman and Kendall-Tau correlation scores between PersonaScore and huma

**判定**: ___　　**理由**: ___

### Simulation_Target
**定义**: 模拟的对象: Client Agent / Therapist Agent / Dual-Agent / Human Trainee

| cxt | hyh |
|-----|-----|
| HUMAN TRAINEE/DUAL-AGENT | PERSONA AGENT |

**eval_report 证据**: Persona agents, which are LLM agents conditioned to act according to an assigned persona, enable contextually rich and user-aligned interactions across domains like education and healthcare.

**判定**: ___　　**理由**: ___

### Uses_Standard_Metrics
**定义**: 是否使用了标准/公认的评估指标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: PersonaScore, the first automatic metric to our knowledge to quantify the capabilities of persona agents on five agent evaluation tasks. ... These five tasks are all grounded in decision theory and make up the different decision aspects of persona agents.

**判定**: ___　　**理由**: ___

---
## Paper 102　（5 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| DYNAMIC | PATTERN-LEVEL |

**eval_report 证据**: We calculated the average positive and nega- tive emotional fluctuations of participants when in- teracting with three different systems: EmoLLM (Yang et al., 2024), CACTUS (Lee et al., 2024), MIND, and a control group. ... Across 70 samples (10 per theme for 7 themes), the proportion of failed cases- defined as instances where user thoughts were not fully shifted within 10 rounds-decreased only s

**判定**: ___　　**理由**: ___

### Has_Longitudinal_Eval
**定义**: 是否包含纵向/长期评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Participants entered a real counseling room and engaged in ﬁve rounds of text-based conversations with the assigned model via a computer. The content of the conversations was kept strictly conﬁdential, and the model stopped recording as soon as the conversations were over. ... To assess changes in clients' emotional states, we employed the Positive and Negative Affect Schedule (PANAS) questionnair

**判定**: ___　　**理由**: ___

### Prompt_Disclosure
**定义**: 提示词披露度: Full（清晰提供了所有必要提示词，原则上可复现）/ Partial（展示了部分提示词，不足以复现）/ No（没有可用的提示词信息）

| cxt | hyh |
|-----|-----|
| FULL | PARTIAL |

**eval_report 证据**: Detailed prompt templates used by each agent are presented in Appendix F. ... In this section, we present some prompt templates used in this work, and its ablated versions.

**判定**: ___　　**理由**: ___

### Theory_Grounding
**定义**: 理论支撑度: Strong（明确使用公认理论来定义或测量）/ Weak（提及了概念但未在评估中实际操作化）/ None（没有真正的理论支撑）

| cxt | hyh |
|-----|-----|
| STRONG | WEAK |

**eval_report 证据**: Emotional Relief: 'Focus on the effectiveness of the framework: Determine whether the framework successfully alleviates the user's emotions.' Reference: (Gross;, 1998). ... Immersion: Measures whether the user feels fully engaged and captivated by the interaction. ... Focus on game scenario construction: Assess the level of player immersion within the game narrative. (Jennett et al., 2008) ... Eng

**判定**: ___　　**理由**: ___

### Theory_Operationalized
**定义**: 理论操作化程度: Strong（评估标准明确源于理论）/ Partial（理论被提及并部分操作化）/ Mentioned（理论仅被提及，未操作化）/ None（没有使用任何理论）

| cxt | hyh |
|-----|-----|
| STRONG | PARTIAL |

**eval_report 证据**: Emotional Relief Measures if the interac- tion reduces user stress or anxiety. Focus on the effectiveness of the framework: Determine whether the framework successfully alle- viates the user’s emotions. (Gross;, 1998) ... Immersion Measures whether the user feels fully engaged and captivated by the interaction. Focus on game scenario con- struction: Assess the level of player immersion within the 

**判定**: ___　　**理由**: ___

---
## Paper 104　（11 个分歧）

### Coding Options
**定义**: 是否明确报告了评估者之间的一致性: Yes / No / N/A

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Over multiple rounds, the experts provided their ratings and justifications for each category. After each round, a facilitator collated the responses, thereby presenting an anonymous summary of the panel's ratings and reasoning. ... The average score for each category was computed.

**判定**: ___　　**理由**: ___

### Dataset_Available
**定义**: 数据集是否公开可用（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: Data Availability Statement: Data are contained within the article.

**判定**: ___　　**理由**: ___

### Fidelity
**定义**: 是否符合预设角色/目标（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: Table 1. Performance evaluation of our custom GPT in several categories of occupational therapy. ... Overall Effectiveness as a Therapeutic Tool 4.1 ... Meaningful Contributions to Therapy 4.0 ... Suitability for Diverse Patient Groups 3.3 ... Recommendation for Clinical Use 3.8

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: This table shows how ChatGPT performed when the ten therapists used different prompts to assess its effectiveness across various standard metrics in these treatments.

**判定**: ___　　**理由**: ___

### Has_Rubric
**定义**: 是否提供了明确的评分标准/评分指引（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: A rating scale from 1 (representing inferior performance) to 5 (indicating excellent performance) was employed to quantify the model's performance. Over multiple rounds, the experts provided their ratings and justifications for each category. After each round, a facilitator collated the responses, thereby presenting an anonymous summary of the panel's ratings and reasoning.

**判定**: ___　　**理由**: ___

### Interaction_Level
**定义**: 交互层级: Single-turn / Short Multi-turn（2-5轮）/ Extended Dialogue（6+轮）/ Longitudinal（跨会话）

| cxt | hyh |
|-----|-----|
| SINGLE-TURN | SHORT MULTI-TURN |

**eval_report 证据**: They assessed each category by interacting with questions and simulated events through a specialized interface, which offered a realistic simulation of how the robot would react to specific inputs, including behavioral events exhibited by the child or commands inputted through the robotic assistant's interface. ... Figure 3 shows examples of the interaction between ChatGPT and the therapists to me

**判定**: ___　　**理由**: ___

### Prompt_Disclosure
**定义**: 提示词披露度: Full（清晰提供了所有必要提示词，原则上可复现）/ Partial（展示了部分提示词，不足以复现）/ No（没有可用的提示词信息）

| cxt | hyh |
|-----|-----|
| PARTIAL | NO |

**eval_report 证据**: It details the required information, including the therapist's name, a description of the custom ChatGPT's functionalities, initial prompts as instructions, and supplementary knowledge provided in PDF files.

**判定**: ___　　**理由**: ___

### Realism
**定义**: 输出是否像人类或自然（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: Table 1. Performance evaluation of our custom GPT in several categories of occupational therapy. ... Clarity and Comprehensibility of Communication 4.7 ... Coherence and Relevance in Conversation 4.6 ... Engaging and Motivational Language Usage 4.7

**判定**: ___　　**理由**: ___

### Sim_Behavior_Realistic
**定义**: 模拟行为是否真实（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: A panel of ten esteemed experts in therapies for children with ADHD was assembled and presented with various prompts to gauge ChatGPT's performance. They assessed each category by interacting with questions and simulated events through a specialized interface, which offered a realistic simulation of how the robot would react to specific inputs. The evaluation assesses ChatGPT's therapeutic respons

**判定**: ___　　**理由**: ___

### Theory_Operationalized
**定义**: 理论操作化程度: Strong（评估标准明确源于理论）/ Partial（理论被提及并部分操作化）/ Mentioned（理论仅被提及，未操作化）/ None（没有使用任何理论）

| cxt | hyh |
|-----|-----|
| MENTIONED | PARTIAL |

**eval_report 证据**: The results from evaluating ChatGPT are summarized in Table 1. This table shows how ChatGPT performed when the ten therapists used different prompts to assess its effectiveness across various standard metrics in these treatments [48,49]. ... The Delphi method [47] was meticulously applied to evaluate ChatGPT's efficacy across several vital categories crucial for conducting therapy sessions with ch

**判定**: ___　　**理由**: ___

### Uses_Standard_Metrics
**定义**: 是否使用了标准/公认的评估指标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: This table shows how ChatGPT performed when the ten therapists used different prompts to assess its effectiveness across various standard metrics in these treatments [48,49].

**判定**: ___　　**理由**: ___

---
## Paper 106　（2 个分歧）

### Fidelity
**定义**: 是否符合预设角色/目标（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: (2) CBT Structure Measure, assessing whether the answer adheres to specific CBT structures and principles, with scores ranging from 0-2, indicating from not adhering to structure to fully adhering;

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Our experiments demonstrate the superiority of our CBT-LLM model in the domain of mental health support Q&A tasks, outperforming three advanced benchmark models. ... Table 4: Automatic evaluation results on CBT QA dataset

**判定**: ___　　**理由**: ___

---
## Paper 107　（6 个分歧）

### Coding Options
**定义**: 是否明确报告了评估者之间的一致性: Yes / No / N/A

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We recruit three mental health practitioners. We ask them to rate the models' outputs on test set examples based on their reliability and helpfulness on a 1 to 5 scale. ... We find that our proposed model achieves the highest relatability and helpfulness ratings.

**判定**: ___　　**理由**: ___

### Emotional Plausibility
**定义**: 情绪反应是否真实/恰当（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: To measure empathy, we build upon the empathy classification model presented in Sharma et al. (2020b). This RoBERTa-based model leverages a theoretically-grounded framework of empathy consisting of three empathy communication mechanisms (emotional reactions, interpretations and explorations) and predicts empathy levels in mental health conversations on a scale from 0 to 6. ... Positivity. To measu

**判定**: ___　　**理由**: ___

### Fidelity
**定义**: 是否符合预设角色/目标（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: We assess the two key reframing outcome metrics of relatability (how relatable would a reframed thought be) and helpfulness (how helpful would a reframed thought be in overcoming negative thoughts). We recruit three mental health practitioners. We ask them to rate the models' outputs on test set examples based on their reliability and helpfulness on a 1 to 5 scale. ... We find that our proposed mo

**判定**: ___　　**理由**: ___

### Human Learning / Outcomes
**定义**: 是否带来人类进步/改变（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: Psychotherapy literature (Beck, 1976) highlights three desirable outcomes for a successful reframe: (a) the reframed thought must be relatable to the individual, (b) it must help them overcome the negative thought and (c) it must be memorable the next time a similar negative thinking pattern emerges. ... We find that reframes with higher actionability are 7.9% more memorable than lower actionabili

**判定**: ___　　**理由**: ___

### Reliability_Reported
**定义**: 是否报告了标准化评估者间信度系数（如 Cohen's kappa, ICC）: Yes / No / N/A。注意：仅报告百分比一致不算

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We recruit three mental health practitioners. We ask them to rate the models' outputs on test set examples based on their reliability and helpfulness on a 1 to 5 scale. We find that our proposed model achieves the highest relatability and helpfulness ratings.

**判定**: ___　　**理由**: ___

### Simulation_Target
**定义**: 模拟的对象: Client Agent / Therapist Agent / Dual-Agent / Human Trainee

| cxt | hyh |
|-----|-----|
| HUMAN TRAINEE/REFRAMING ASSISTANT | HUMAN TRAINEE |

**eval_report 证据**: we conduct a human-centered study of how language models may assist people in reframing negative thoughts. ... we deploy a month-long randomized field study on Mental Health America (MHA; a popular website that shares mental health resources and tools online), with 2,067 participants with informed consent. The system is designed to help individuals learn and practice cognitive reframing — the huma

**判定**: ___　　**理由**: ___

---
## Paper 108　（6 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| DYNAMIC | STATIC |

**eval_report 证据**: We randomly sample 100 dialogues from three test sets (Dt), ensuring diversity (e.g., strategy), and three annotators are required to determine the Win/Tie/Lose for each comparison ... Additionally, we ask three annotators to evaluate each sample on a 1-5 Likert scale, providing specific rubrics for each score to ensure detailed assessments on the quality of responses (Table 5).

**判定**: ___　　**理由**: ___

### Eval_Human_Experts
**定义**: 领域专家（治疗师、临床医生、受过训练的标注员）进行评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We employ human evaluation, outsourcing the task to assess response quality on Amazon Mechanical Turk (AMT). ... in collaboration with four psychologists, we develop a specific set of criteria focused on assessing whether a response provide effective emotional support

**判定**: ___　　**理由**: ___

### Eval_Lay_Users
**定义**: 非专家/普通用户进行评估（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: We employ human evaluation, outsourcing the task to assess response quality on Amazon Mechanical Turk (AMT). ... For each evaluation, we ask three human annotator to assess 100 samples each based on four specified criteria.

**判定**: ___　　**理由**: ___

### Eval_User_Study
**定义**: 结构化实验，用户与系统发生交互（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We employ human evaluation, outsourcing the task to assess response quality on Amazon Mechanical Turk (AMT). ... For each evaluation, we ask three human annotator to assess 100 samples each based on four specified criteria.

**判定**: ___　　**理由**: ___

### Interaction_Level
**定义**: 交互层级: Single-turn / Short Multi-turn（2-5轮）/ Extended Dialogue（6+轮）/ Longitudinal（跨会话）

| cxt | hyh |
|-----|-----|
| EXTENDED DIALOGUE | SHORT MULTI-TURN |

**eval_report 证据**: we randomly truncate the dialogues into 5-15 turns samples. We then annotate each sample with a stage and classify the samples according to their stage.

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| EXPERT PRINCIPLES | SURFACE PERSONA |

**eval_report 证据**: We formulate the emotional support response generation task as generating a response over a support strategy. Formally, given the dialogue background I, a pre-chat survey from the seeker (e.g., emotion, situation), and the dialogue context C, the model θ first predicts the strategy S, and then generates the response R based on I, C, and S

**判定**: ___　　**理由**: ___

---
## Paper 109　（4 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| DYNAMIC | STATIC |

**eval_report 证据**: We first annotate the question topics, dialogue acts (i.e., empathy behaviors and in-depth questions) in the dialogue history ... Accordingly, we calculated the average proportion of question topics of different doctor chatbots, as well as human doctors.

**判定**: ___　　**理由**: ___

### Dataset_Available
**定义**: 数据集是否公开可用（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The symptom list is summarized by ChatGPT and revised by psychiatrists. See Appendix C for details. ... We will provide the full list in the Appendix.

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we focus on exploring the potential of ChatGPT in powering chatbots for psychiatrist and patient simulation. ... Our findings demonstrate the feasibility of using ChatGPT-powered chatbots in psychiatric scenarios and explore the impact of prompt designs on chatbot behavior and user experience.

**判定**: ___　　**理由**: ___

### Uses_Dynamic_State
**定义**: 是否使用动态状态建模（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we focus on exploring the potential of ChatGPT in powering chatbots for psychiatrist and patient simulation. ... The system message serves as an instruction for ChatGPT, providing information about the task and some specific requirements needed to generate an appropriate response.

**判定**: ___　　**理由**: ___

---
## Paper 110　（8 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| DYNAMIC | STATIC |

**eval_report 证据**: The accuracy of each models is presented in Figure 2: Claude-3.5 62.1% ± 3.3 ... The doctor agent is allowed N=20 patient and measurement interactions before a diagnosis must be made.

**判定**: ___　　**理由**: ___

### Coding Options
**定义**: 是否明确报告了评估者之间的一致性: Yes / No / N/A

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We present results from three human clinicians (individuals with MDs) who rated dialogues from 20 agents on AgentClinic-MedQA from 1-10 across four axes ... We find the average ratings from evaluators for each category as follows: Doctor 6.2, Patient 6.7, Measurement 6.3, and Empathy 5.8

**判定**: ___　　**理由**: ___

### Eval_Automatic
**定义**: 算法/数学公式自动计算的指标（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: The accuracy of each models is presented in Figure 2: Claude-3.5 62.1% ± 3.3, OpenBioLLM-70B 58.3 ± 4.2, Human Physicians 54 ± 28.5, GPT-4 at 51.6% ± 3.3

**判定**: ___　　**理由**: ___

### Has_Longitudinal_Eval
**定义**: 是否包含纵向/长期评估（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: The accuracy of each models is presented in Figure 2: Claude-3.5 62.1% ± 3.3, OpenBioLLM-70B 58.3 ± 4.2, Human Physicians 54 ± 28.5, GPT-4 at 51.6% ± 3.3 ... We test decreasing the time to N=10 and N=15 as well as increasing the time to values of to N=25 and N=30.

**判定**: ___　　**理由**: ___

### Reliability_Reported
**定义**: 是否报告了标准化评估者间信度系数（如 Cohen's kappa, ICC）: Yes / No / N/A。注意：仅报告百分比一致不算

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: We present results from three human clinicians (individuals with MDs) who rated dialogues from 20 agents on AgentClinic-MedQA from 1-10 across four axes ... We find the average ratings from evaluators for each category as follows: Doctor 6.2, Patient 6.7, Measurement 6.3, and Empathy 5.8

**判定**: ___　　**理由**: ___

### Theory_Grounding
**定义**: 理论支撑度: Strong（明确使用公认理论来定义或测量）/ Weak（提及了概念但未在评估中实际操作化）/ None（没有真正的理论支撑）

| cxt | hyh |
|-----|-----|
| STRONG | WEAK |

**eval_report 证据**: Cognitive biases are systematic patterns of deviation from norm or rationality in judgment, where individuals draw inferences about situations in an illogical fashion (Blumenthal-Barby & Krieger, 2015). ... Implicit biases are associations held by individuals that operate unconsciously and can influence judgments and behaviors towards various social groups (FitzGerald & Hurst, 2017).

**判定**: ___　　**理由**: ___

### Theory_Operationalized
**定义**: 理论操作化程度: Strong（评估标准明确源于理论）/ Partial（理论被提及并部分操作化）/ Mentioned（理论仅被提及，未操作化）/ None（没有使用任何理论）

| cxt | hyh |
|-----|-----|
| STRONG | PARTIAL |

**eval_report 证据**: Cognitive biases are systematic patterns of deviation from norm or rationality in judgment, where individuals draw inferences about situations in an illogical fashion (Blumenthal-Barby & Krieger, 2015). ... Implicit biases are associations held by individuals that operate unconsciously and can influence judgments and behaviors towards various social groups (FitzGerald & Hurst, 2017). ... These bia

**判定**: ___　　**理由**: ___

### Uses_Dynamic_State
**定义**: 是否使用动态状态建模（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Four language agents are used in the AgentClinic benchmark: a patient agent, doctor agent, measurement agent, and a moderator (Figure 1). Each language agent has specific instructions and is provided unique information that is only available to that particular agent. ... The doctor agent is allowed N=20 patient and measurement interactions before a diagnosis must be made.

**判定**: ___　　**理由**: ___

---
## Paper 111　（6 个分歧）

### Dataset_Available
**定义**: 数据集是否公开可用（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we commit to publicly sharing all data after the paper is accepted.

**判定**: ___　　**理由**: ___

### Has_Robustness_Testing
**定义**: 是否在不同条件下进行了鲁棒性测试（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: we introduce a dataset for Multi-Session Psychological Counseling Conversation Dataset (MusPsy-Dataset) ... we also developed our MusPsy-Model, which aims to track client progress and adapt its counseling direction over time. Experiments show that our model performs better than baseline models across multiple sessions.

**判定**: ___　　**理由**: ___

### Human Learning / Outcomes
**定义**: 是否带来人类进步/改变（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: we measure changes in clients' emotional states using the Positive and Negative Affect Schedule (PANAS) ... our MusPsy-Model effectively reduces negative emotions and enhances positive emotions in the long term ... MusPsy-Model demonstrates a continuous improvement in the client's state

**判定**: ___　　**理由**: ___

### Persona_Model_Depth
**定义**: 模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles

| cxt | hyh |
|-----|-----|
| COGNITIVE MODEL/DYNAMIC TRAITS | DYNAMIC TRAITS |

**eval_report 证据**: Client profiles are composed of static traits and dynamic states. ... Static Traits: These include pseudonym, gender, age, occupation, and initial psychological issues reported during intake. ... Dynamic States: These capture session-by-session changes, including the client's evolving recent life events and emotional and cognitive state.

**判定**: ___　　**理由**: ___

### Realism
**定义**: 输出是否像人类或自然（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: Coherence: the logical consistency in the conversation. ... Realism concerns raised by LLM: We acknowledge that despite our efforts to pursue realism by using authentic case reports, we cannot fully resolve the issue of realism.

**判定**: ___　　**理由**: ___

### Simulation_Target
**定义**: 模拟的对象: Client Agent / Therapist Agent / Dual-Agent / Human Trainee

| cxt | hyh |
|-----|-----|
| DUAL-AGENT | THERAPIST AGENT |

**eval_report 证据**: We train an automated psychological counseling model using the MusPsy-Dataset to conduct multi-session counseling.

**判定**: ___　　**理由**: ___

---
## Paper 112　（4 个分歧）

### Behavior_Eval_Depth
**定义**: 行为评估深度: Dynamic（分析了行为如何随轮次变化）/ Pattern-level（统计行为频率/模式，不关心变化）/ Static（每轮独立评分，不看轮次间关系）/ None（完全不涉及行为）

| cxt | hyh |
|-----|-----|
| DYNAMIC | STATIC |

**eval_report 证据**: Performance of listening skills was assessed at 6 different time points during the study: before training began, during open question training, during reflection training, during combined reflection and open question training, after feedback was removed, and performance on fixed prompts on the posttest

**判定**: ___　　**理由**: ___

### Coding Options
**定义**: 是否明确报告了评估者之间的一致性: Yes / No / N/A

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: Each transcript was rated using the MI skills code (MISC) [39] ... The kappa scores for the machine-human agreement ranged between .39 and .79.

**判定**: ___　　**理由**: ___

### Comparable_To_Prior_Work
**定义**: 评估是否可与先前研究进行对比（YES/NO）

| cxt | hyh |
|-----|-----|
| NO | YES |

**eval_report 证据**: There is strong evidence that providing ongoing performance-based feedback via behavioral coding to therapists results in skills acquisition and retention (eg, [8]). However, this process is slow and labor intensive (eg, in some cases 4 or 5 times the length of the session) [9].

**判定**: ___　　**理由**: ___

### Fidelity
**定义**: 是否符合预设角色/目标（YES/NO）

| cxt | hyh |
|-----|-----|
| YES | NO |

**eval_report 证据**: There was a general sense among the participants of the study that the simulated patient was not a realistic substitute for another human. The computerized dialogue model could sometimes say distracting or irrelevant responses. ... it responds with the phrase "I don't know" relatively frequently ... it responds in ways that would be contextually rare in psychotherapy, such as "I love you."

**判定**: ___　　**理由**: ___
