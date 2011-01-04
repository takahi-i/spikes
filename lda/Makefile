#================================================================
# Setting Variables
#================================================================

# Generic settings
PYTHON=python
ALPHA=1.0
BETA=0.001
ITERATIONS=10000
MODEL_PREFIX=model
TRAIN_FILE=train_large
INFER_FILE=test_large
ONLINE_INFER_FILE=test_online_large
TOPIC_NUM=10

# Targets

learn:
	$(PYTHON) lda_learn.py -r $(ITERATIONS) -m $(MODEL_PREFIX) -i $(TRAIN_FILE) -n $(TOPIC_NUM) -a $(ALPHA) -b $(BETA)

infer: 
	$(PYTHON) lda_infer.py -r $(ITERATIONS) -m $(MODEL_PREFIX) -i $(INFER_FILE)

oinfer: 
	$(PYTHON) lda_online_inference.py -r $(ITERATIONS) -m $(MODEL_PREFIX) -i $(ONLINE_INFER_FILE)

recommend: 
	$(PYTHON) lda_recommend.py -r $(ITERATIONS) -m $(MODEL_PREFIX) -i $(ONLINE_INFER_FILE)

clean :
	rm -rf $(COMMANDFILES) $(MODEL_PREFIX).* *~ *.pyc

# End of file
