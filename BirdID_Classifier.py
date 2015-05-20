#!/usr/bin/env python
""" Classify bird images

Using a model trained by phow_train.py, redistribute images from an input
directory to a series of new directories corresponding to the classes
of images distinguished by the model.
"""

import ttk
import Tkinter as tk
import tkFileDialog as tkfd
from datetime import datetime
from os import mkdir, listdir
from os.path import exists, join, basename
from shutil import copyfile
from scipy.io import loadmat
from sklearn.kernel_approximation import AdditiveChi2Sampler
from cPickle import load
import birdid_utils

VERBOSE = True

class Application(ttk.Frame):
    """ Main application class """

    debug = True

    # Button text strings - doing it this way lets you change the button
    # text on the fly by just reassinging the value of the variable
    quitButtonText = 'Quit'

    modelLabelText = 'Model directory'
    modelDirBrowseButtonText = '...'
    modelDirBrowseTitle = 'Choose directory containing model'

    modelIdentifierLabelText = 'Model identifier'
    modelSelectDefault = 'None Selected'

    modelPrefixLabelText = 'Model prefix'

    imageLabelText = 'Image directory'
    imageDirBrowseButtonText = '...'
    imageDirBrowseTitle = 'Choose directory containing images'

    destLabelText = 'Destination directory'
    destDirBrowseButtonText = '...'
    destDirBrowseTitle = 'Choose directory for classified images'

    classifyButtonText = 'Classify'

    statusLabelText = 'Status'

    # Text field width
    entryWidth = 40

    # Widget padding
    widgetPadX = 4
    widgetPadY = 3

    def __init__(self, master=None):
        self.selectedPrefix = ''

        ttk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

        # Setup to allow widgets to grow upon resizing
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
    	# top.columnconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)

    	# directory for loading model
        col = 0
        row = 0
        self.modelDirLabel = ttk.Label(self, text=self.modelLabelText)
        self.modelDirLabel.grid(row=row, column=col,
                                padx=self.widgetPadX, pady=self.widgetPadY,
                                sticky=tk.E)
        col += 1

        self.modelDirEntryText = tk.StringVar()
        self.modelDirEntryText.set('')
        self.modelDirEntry = ttk.Entry(self,
                                       textvariable=self.modelDirEntryText,
                                       width=self.entryWidth)
        self.modelDirEntry.grid(row=row, column=col, columnspan=3,
                                padx=self.widgetPadX, pady=self.widgetPadY,
                                sticky=tk.W+tk.E)
        col += 3

        self.modelDirBrowseButton = \
            ttk.Button(self, text=self.modelDirBrowseButtonText,
                       command=self.modelDirBrowse)
        self.modelDirBrowseButton.grid(row=row, column=col,
                                       padx=self.widgetPadX,
                                       pady=self.widgetPadY)

        row += 1
        col = 0

        # Model identifier selection. There can be multiple models with
        # different identifiers stored in the same directory
        self.modelIdentifierLabel = \
            ttk.Label(self,
                      text=self.modelIdentifierLabelText)
        self.modelIdentifierLabel.grid(
            row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.E)
        col += 1

        self.modelIdentifierCombo = \
            ttk.Combobox(self, height=30,
                         justify=tk.LEFT, values=[self.modelSelectDefault],
                         state='disabled')
        self.modelIdentifierCombo.current(0)
        self.modelIdentifierCombo.bind('<<ComboboxSelected>>',
                                       self.handleModelSelection)
        self.modelIdentifierCombo.grid(
            row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.W+tk.E)
        col += 1

        # Model prefix selection. Each identifier can have multiple prefixes
        # associated with it.
        self.modelPrefixLabel = \
            ttk.Label(self, text=self.modelPrefixLabelText)
        self.modelPrefixLabel.grid(
            row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.E)
        col += 1

        self.modelPrefixCombo = \
            ttk.Combobox(self, height=15,
                         justify=tk.LEFT, values=[self.modelSelectDefault],
                         state='disabled')
        self.modelPrefixCombo.current(0)
        self.modelPrefixCombo.bind('<<ComboboxSelected>>',
                                   self.handleModelPrefixSelection)
        self.modelPrefixCombo.grid(
            row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.W+tk.E)

        row += 1
        col = 0

        # directory holding images
        self.imageDirLabel = ttk.Label(self, text=self.imageLabelText)
        self.imageDirLabel.grid(
            row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.E)
        col += 1

        self.imageDirEntryText = tk.StringVar()
        self.imageDirEntryText.set('')
        self.imageDirEntry = \
            ttk.Entry(self, textvariable=self.imageDirEntryText,
                      width=self.entryWidth)
        self.imageDirEntry.grid(
            row=row, column=col, columnspan=3,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.W+tk.E)
        col += 3

        self.imageDirBrowseButton = \
            ttk.Button(self, text=self.imageDirBrowseButtonText,
                       command=self.imageDirBrowse)
        self.imageDirBrowseButton.grid(
            row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY)

        row += 1
        col = 0

        # destination directory for classified images
        self.destDirLabel = ttk.Label(self, text=self.destLabelText)
        self.destDirLabel.grid(
            row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.E)
        col += 1

        self.destDirEntryText = tk.StringVar()
        self.destDirEntryText.set('')
        self.destDirEntry = ttk.Entry(
            self, textvariable=self.destDirEntryText,
            width=self.entryWidth)
        self.destDirEntry.grid(
            row=row, column=col, columnspan=3,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.W+tk.E)
        col += 3

        self.destDirBrowseButton = \
            ttk.Button(self, text=self.destDirBrowseButtonText,
                       command=self.destDirBrowse)
        self.destDirBrowseButton.grid(
            row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY)

        row += 1
        col = 0

        self.classifyButton = ttk.Button(
            self,
            text=self.classifyButtonText,
            command=self.classifyImages)
        self.classifyButton.grid(
            row=row, column=col, columnspan=5,
            padx=self.widgetPadX, pady=self.widgetPadY)

        row += 1
        col = 0

        separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        separator.grid(
            row=row, column=col, columnspan=5,
            pady=self.widgetPadY, sticky=tk.W+tk.E)

        row += 1
        col = 0

        # Status area
        self.statusFrame = ttk.LabelFrame(
            self, text=self.statusLabelText,
            borderwidth=5, relief=tk.GROOVE)
        self.statusFrame.grid(
            row=row, column=col, columnspan=5,
            padx=self.widgetPadX, pady=self.widgetPadY,
            sticky=tk.N+tk.S+tk.E+tk.W)
        self.rowconfigure(row, weight=1)
        self.statusFrame.rowconfigure(0, weight=1)
        self.statusFrame.columnconfigure(0, weight=1)

        self.statusField = tk.Text(self.statusFrame, height=10)
        self.statusField.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        scrl = ttk.Scrollbar(self.statusFrame, command=self.statusField.yview)
        self.statusField.config(yscrollcommand=scrl.set)
        scrl.grid(row=0, column=1, sticky='ns')

        row += 1
        col = 0

     	#self.rowconfigure(row, weight=1)
    	#self.columnconfigure(col, weight=1)
        self.quitButton = ttk.Button(
            self, text=self.quitButtonText,
            command=self.quit)
        self.quitButton.grid(
            row=row, column=col, columnspan=5,
            padx=self.widgetPadX, pady=self.widgetPadY)
        #self.quitButton.grid(column=col, row=row, sticky=tk.S+tk.E+tk.W)

    def updateStatus(self, message):
        self.statusField.insert('end', message + '\n')
        return

    def modelDirBrowse(self):
        dirname = self.browseForDir(self.modelDirEntryText,
                                    self.modelDirBrowseTitle)

        if len(dirname) > 0:
            # Update the combobox of available identifiers from the contents
            # of directory dirname
            fileList = listdir(dirname)

            # Debug - print out list of files in the model dir
            if VERBOSE:
                self.updateStatus('Selected model folder ' + dirname)
                print 'Files in model directory'
                for fname in fileList:
                    print fname

            # Put file names into appropriate sequences
            # assumes filenames are presented in lexicographic ordering
            identifier = ''
            prefix = ''
            self.allPrefixes = {}
            self.allIdentifiers = [self.modelSelectDefault]
            self.allHists = []
            self.allVocabs = []
            self.allModels = []

            for fname in fileList:
                if fname.find('hists') >= 0:
                    identifier = fname[0:fname.index('-hists')]
                    self.allIdentifiers.append(identifier)
                    self.allHists.append(fname)
                    self.allPrefixes[identifier] = [self.modelSelectDefault]
                elif fname.find('vocab') >= 0:
                    self.allVocabs.append(fname)
                elif fname.find('model') >= 0:
                    self.allModels.append(fname)
                    identifier = fname[fname.index('-')+1:fname.index('-model')]
                    prefix = fname[0:fname.index('-')]
                    if self.debug:
                        print 'Found prefix ' + prefix + ' for ID ' + \
                            identifier
                    self.allPrefixes[identifier].append(prefix)


            # Update the combo box with the list of available identifiers
            self.modelIdentifierCombo.configure(
                values=self.allIdentifiers,
                state='Enabled')

        return

    def imageDirBrowse(self):
        self.browseForDir(self.imageDirEntryText, self.imageDirBrowseTitle)
        return

    def destDirBrowse(self):
        self.browseForDir(self.destDirEntryText, self.destDirBrowseTitle)
        return

    def browseForDir(self, entryStringVar, titleStr):
        dirname = tkfd.askdirectory(
            parent=self, initialdir='~/',
            title=titleStr)
        entryStringVar.set(dirname)
        return dirname

    def handleModelSelection(self, evt):
        self.selectedIdentifier = evt.widget.get()
        print 'Available prefixes: %s' % \
            str(self.allPrefixes[self.selectedIdentifier])
        self.modelPrefixCombo.configure(
            values=self.allPrefixes[self.selectedIdentifier], state='Enabled')
        # Debugging
        if self.debug:
            print 'Called handleModelSelection()'
            selection = evt.widget.get()
            self.updateStatus('Selected model identifier ' + selection)
        return

    def handleModelPrefixSelection(self, evt):
        self.selectedPrefix = evt.widget.get()

        # Debugging
        if self.debug:
            print 'Called handleModelPrefixSelection()'
            self.updateStatus('Selected model prefix ' + self.selectedPrefix)
        return

    def classifyImages(self):
        # Load configuration from result of training so we're working with
        # the same parameters
        resultFileName = self.selectedPrefix + '-' + self.selectedIdentifier + \
            '-result'
        resultPath = join(self.modelDirEntryText.get(), resultFileName)

        with open(resultPath, 'rb') as fp:
            conf = load(fp)
            classes = load(fp)
            if VERBOSE:
                self.updateStatus(
                    str(datetime.now()) + "Found classes " + str(classes))

        # The Model class is just a subset of the Configuration class wth
        # the set of categories added in. The categories aren't needed for
        # this preprocessing, since they only have an impact on the final
        # classification. We do need the class names to decide how to name
        # the destination folders, however.
        model = birdid_utils.Model([], conf)

        # Load existing model for classification
        modelFileName = self.selectedPrefix + '-' + self.selectedIdentifier + \
            '-model.py.mat'
        modelPath = join(self.modelDirEntryText.get(), modelFileName)

        if VERBOSE:
            self.updateStatus(str(datetime.now()) + ' Loading model from ' +
                              modelFileName)

        with open(modelPath, 'rb') as fp:
            # SVM classifier trained on similar data
            clf = load(fp)

        # Preprocess images to be classified as training model images were
        # preprocessed

        imgPath = self.imageDirEntryText.get()

        # imgs contains the filenames of the files in the requested folder
        imgs = birdid_utils.get_imgfiles(imgPath,
                                         conf.extensions)

        # Use vocabulary extracted from training images
        model.vocab = loadmat(conf.vocabPath)['vocab']

        # Extract vocabulary from images to be classified. This is wrong, as 
        # I suspected. Results in everything being classified as a Cardinal.
        # model.vocab = birdid_utils.trainVocab(range(len(imgs)), imgs, conf)

        # Compute spatial histograms from test images
        self.updateStatus(str(datetime.now()) + " Computing spatial histograms")
        hists = birdid_utils.computeHistograms(imgs, model, conf)

        # Compute feature map of image data
        self.updateStatus(str(datetime.now()) + " Computing feature map")
        transformer = AdditiveChi2Sampler()
        histst = transformer.fit_transform(hists)

        # Classify images using trained model. predicted_clases is an array
        # containing the index for the predicted class of each image
        self.updateStatus(str(datetime.now()) + " Classifying images")
        predicted_classes = clf.predict(histst)

        # Make copies of the classified images in a new folder structure
        # reflecting the identified classes

        # Check that top level destination folder exists and create if not.
        self.updateStatus(
            str(datetime.now()) + " Creating destination folders in")
        destFolder = self.destDirEntryText.get()
        self.updateStatus("    " + destFolder)
        if not exists(destFolder):
            create_dir(destFolder)

        pathToClass = []
        i = 0

        for className in classes:
            self.updateStatus("    " + className)
            pathToClass.append(join(destFolder, className))
            self.updateStatus("    " + pathToClass[i])
            if not exists(pathToClass[i]):
                create_dir(pathToClass[i])
            i += 1

        self.updateStatus("Copying images to destination folders")
        for i in range(len(imgs)):
            destfn = join(pathToClass[predicted_classes[i]], basename(imgs[i]))
            # if self.debug:
            #     print 'imgPath = ' + imgPath
            #     print 'pathToClass[i] = ' + pathToClass[predicted_classes[i]]
            copyfile(imgs[i], destfn)

        return

# Create a directory if it doesn't already exist
def create_dir(dirName):
    try:
        mkdir(dirName)
    except OSError:
        pass

    return

###############
# Main Program
###############

# Allow this file to be imported or run as main program
if __name__ == '__main__':
    app = Application()
    app.master.title('BirdID Classifier')
    app.mainloop()
