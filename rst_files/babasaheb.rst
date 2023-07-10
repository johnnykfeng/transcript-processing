

===================================================
Large-Language Models and Machine Learning Research 
===================================================
*Karim Khayrat* 

Summary 
-------
The presentation discussed the use of large-language models in generating questions and the results of different experiments. It also covered the self-instruct process for generating synthetic instruction datasets and the potential applications in fine-tuning language models. 

Topics: 
-------
	Guided by Bad Questions (GBQ) Method 
		* Large-language models are used to improve the quality of generated questions. 
		* The GBQ method uses examples of bad questions from the MS Marco dataset and manually creates good questions. 
		* The model generates both good and bad questions for each document using the full context of the document. 
		* Questions in the GBQ method are filtered based on the mono T5 model for higher quality filtering. 
	Results of Experiments 
		* The performance of the mono T5 model trained on different datasets did not change significantly, indicating consistent question quality. 
		* The mono T5 model fine-tuned on the MS Marco dataset performed well across different datasets. 
	Few-Shot Learning for Information Retrieval Tasks 
		* The paper proposes a few-shot learning approach for generating synthetic training datasets. 
		* The model generates questions relevant to a document by providing a document and a prefix. 
		* The top examples are selected based on the log probability of the generated output. 
		* The re-ranker is used to fine-tune the dataset by scoring the relevancy of the question and document pairs. 
	Alpaca 7 Billion Model 
		* The Alpaca 7 billion model is a fine-tuned model using the self-instruct process. 
		* It performs similarly to OpenAI's DaVinci model but is smaller and cheaper to reproduce. 
		* The model has limitations due to its reliance on the original Llama 7 billion model. 
