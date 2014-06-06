#!/usr/bin/env python
import ttk
import Tkinter as tk
import tkFileDialog as tkfd
import os

class Application(ttk.Frame):
    debug=true

    # Button text strings - doing it this way lets you change the button
    # text on the fly by just reassinging the value of the variable
    quitButtonText = 'Quit'

    modelLabelText = 'Model directory'
    modelDirBrowseButtonText = '...'
    modelDirBrowseTitle = 'Choose directory containing model'

    modelIdentifierLabelText = 'Model identifier'

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
        ttk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.createWidgets()

    def createWidgets(self):
        # Setup to allow widgets to grow upon resizing
    	top=self.winfo_toplevel()
    	top.rowconfigure(0, weight=1)
    	top.columnconfigure(0, weight=1)

    	# directory for loading model
    	col = 0
    	row = 0
        self.modelDirLabel = ttk.Label(self, text=self.modelLabelText)
        self.modelDirLabel.grid(row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.E)
        col += 1

        self.modelDirEntryText = tk.StringVar()
        self.modelDirEntryText.set('')
        self.modelDirEntry = ttk.Entry(self, textvariable=self.modelDirEntryText,
            width=self.entryWidth)
        self.modelDirEntry.grid(row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY)
        col += 1

        self.modelDirBrowseButton = ttk.Button(self, 
            text=self.modelDirBrowseButtonText,
            command=self.modelDirBrowse)
        self.modelDirBrowseButton.grid(row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY)

        row += 1
        col = 0

        # Model identifier selection. There can be multiple models with
        # different identifiers stored in the same directory
        self.modelIdentifierLabel = ttk.Label(self, 
            text=self.modelIdentifierLabelText)
        self.modelIdentifierLabel.grid(row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.E)
        col += 1

        self.modelIdentifierCombo = ttk.Combobox(self, height=30, 
            justify=tk.LEFT)
        self.modelIdentifierCombo.bind('<<ComboboxSelected>>', self.handleModelSelection)
        self.modelIdentifierCombo.grid(row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.W)

        row += 1
        col = 0

        # directory holding images
        self.imageDirLabel = ttk.Label(self, text=self.imageLabelText)
        self.imageDirLabel.grid(row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.E)
        col += 1

        self.imageDirEntryText = tk.StringVar();
        self.imageDirEntryText.set('')
        self.imageDirEntry = ttk.Entry(self, textvariable=self.imageDirEntryText,
            width=self.entryWidth)
        self.imageDirEntry.grid(row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY)
        col += 1

        self.imageDirBrowseButton = ttk.Button(self, 
            text=self.imageDirBrowseButtonText,
            command=self.imageDirBrowse)
        self.imageDirBrowseButton.grid(row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY)

        row += 1
        col = 0

        # destination directory for classified images
        self.destDirLabel = ttk.Label(self, text=self.destLabelText)
        self.destDirLabel.grid(row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY, sticky=tk.E)
        col += 1

        self.destDirEntryText = tk.StringVar();
        self.destDirEntryText.set('')
        self.destDirEntry = ttk.Entry(self, textvariable=self.destDirEntryText,
            width=self.entryWidth)
        self.destDirEntry.grid(row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY)
        col += 1

        self.destDirBrowseButton = ttk.Button(self, 
            text=self.destDirBrowseButtonText,
            command=self.destDirBrowse)
        self.destDirBrowseButton.grid(row=row, column=col,
            padx=self.widgetPadX, pady=self.widgetPadY)

        row += 1
        col = 0

        self.classifyButton = ttk.Button(self, 
            text=self.classifyButtonText,
            command=self.classifyImages)
        self.classifyButton.grid(row=row, column=col, columnspan=3,
            padx=self.widgetPadX, pady=self.widgetPadY)

        row += 1
        col = 0

        separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        separator.grid(row=row, column=col, columnspan=3,
            pady=self.widgetPadY, sticky=tk.W+tk.E)

        row += 1
        col = 0

        self.statusFrame = ttk.LabelFrame(self, text=self.statusLabelText,
            borderwidth=5, relief=tk.GROOVE)
        self.statusFrame.grid(row=row, column=col, columnspan=3,
            padx=self.widgetPadX, pady=self.widgetPadY)

        self.statusField = tk.Text(self.statusFrame, height=10)
        self.statusField.grid(row=0, column=0)

        row += 1
        col = 0

     	#self.rowconfigure(row, weight=1)
    	#self.columnconfigure(col, weight=1)
        self.quitButton = ttk.Button(self, text=self.quitButtonText,
            command=self.quit)
        self.quitButton.grid(row = row, column=col, columnspan=3,
            padx=self.widgetPadX, pady=self.widgetPadY)
        #self.quitButton.grid(column=col, row=row, sticky=tk.S+tk.E+tk.W)

    def modelDirBrowse(self):
        dirname = self.browseForDir(self.modelDirEntryText, 
            self.modelDirBrowseTitle)

        if len(dirname) > 0:
            # Update the combobox of available identifiers from the contents
            # of directory dirname
            fileList = os.listdir(dirname)

            # Debug - print out list of files in the model dir
            if debug:
                self.statusField.insert('end', '\nSelected model folder ' + dirname)
                print 'Files in model directory'
                for fname in fileList:
                    print fname

            # Put file names into appropriate sequences
            # assumes filenames are presented in lexicographic ordering
            identifier = ''
            prefix = ''
            self.allIdentifiers = []
            self.allHists = []
            self.allVocabs = []
            self.allModels = []

            for fname in fileList:
                if fname.find('hists') >= 0:
                    identifier = fname[0:fname.index('-hists')]
                    self.allIdentifiers.append(identifier)
                    self.allHists.append(fname)
                elif fname.find('vocab') >= 0:
                    self.allVocabs.append(fname)
                elif fname.find('model') >= 0:
                    self.allModels.append(fname)

            # Update the combo box with the list of available identifiers
            self.modelIdentifierCombo.configure(values=self.allIdentifiers)

        return

    def imageDirBrowse(self):
        self.browseForDir(self.imageDirEntryText, self.imageDirBrowseTitle)
        return

    def destDirBrowse(self):
        self.browseForDir(self.destDirEntryText, self.destDirBrowseTitle)
        return

    def browseForDir(self, entryStringVar, titleStr):
        dirname = tkfd.askdirectory(parent=self, initialdir='~/',
            title=titleStr)
        entryStringVar.set(dirname)
        return dirname

    def handleModelSelection(self, evt):
        # Debugging
        if debug:
            print 'Called handleModelSelection()'
            selection = evt.widget.get()
            self.statusField.insert('end', '\nSelected ' + selection)
        return

    def classifyImages(self):
        return

app = Application()
app.master.title('BirdID Classifier')
app.mainloop()