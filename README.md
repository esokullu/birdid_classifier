# birdid_classifier
Program that uses a previously trained SVM model to classify images.

This is based on the phow_caltech101 scripts from vlfeat.org. It basically takes a folder of unclassified
and a previously trained model and tries to classify the new images into the appropriate categories. 
It does not currently work very well - so there is likely some error in the way it attempts to use the
existing model.
