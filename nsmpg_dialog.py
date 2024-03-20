# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NSMPGDialog
                                 A QGIS plugin
 New implementation of SMPG
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-09-23
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Juan Pablo Diaz Lombana
        email                : email.not@defined.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import time
# import cProfile
# import pstats

# from qgis.PyQt import uic, QtWidgets
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog, QPushButton, QMessageBox, QComboBox, QLineEdit

from .nsmpgCore.parsers.CSVParser import parse_csv
from .nsmpgCore.structures import Dataset, Options, Properties
from .nsmpgCore.commons import define_seasonal_dict, parse_timestamps
from .nsmpgCore.exporters.WebExporter import export_to_web_files

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'nsmpg_dialog_base.ui'))


class NSMPGDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(NSMPGDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        ### My code starting from here
        self.loadFileButton: QPushButton
        self.processButton: QPushButton
        self.datasetInputLineEdit: QLineEdit
        self.climatologyStartComboBox: QComboBox
        self.climatologyEndComboBox: QComboBox
        self.seasonStartComboBox: QComboBox
        self.seasonEndComboBox: QComboBox

        self.datasetInputLineEdit.editingFinished.connect(self.path_changed_event)
        self.datasetInputLineEdit.setPlaceholderText('Select a source dataset.')

        self.loadFileButton.clicked.connect(self.load_file_btn_event)
        self.processButton.clicked.connect(self.process_btn_event)

    # function that reads the dataset from a file.
    def load_file_btn_event(self): 
        # path reading
        self.selected_source = QFileDialog.getOpenFileName(self, 'Open dataset file', None, "CSV files (*.csv)")[0]
        if self.selected_source == "": return
        self.dataset_source_path = os.path.normpath(os.path.dirname(self.selected_source))
        self.dataset_filename = ''.join(os.path.basename(self.selected_source).split('.')[:-1])

        # parse dataset
        self.parsed_dataset, self.col_names = parse_csv(self.selected_source)
        self.dataset_properties = Properties(parse_timestamps(self.col_names))

        # set form fields content from data
        self.datasetInputLineEdit.setText(self.selected_source)

        self.climatologyStartComboBox.clear()
        self.climatologyStartComboBox.addItems(self.dataset_properties.year_ids)
        self.climatologyEndComboBox.clear()
        self.climatologyEndComboBox.addItems(self.dataset_properties.year_ids)
        self.climatologyEndComboBox.setCurrentIndex(len(self.dataset_properties.year_ids)-1)

        seasons = define_seasonal_dict()
        self.seasonStartComboBox.clear()
        self.seasonStartComboBox.addItems(seasons)
        self.seasonEndComboBox.clear()
        self.seasonEndComboBox.addItems(seasons)
        self.seasonEndComboBox.setCurrentIndex(len(seasons)-1)

    # function to allow the computation of the required data, such as accumulation, ensemble, stats, percentiles, etc
    def process_btn_event(self):
        # with cProfile.Profile() as profile:

        renderTime = time.perf_counter()
        self.structured_dataset = Dataset(self.dataset_filename, self.parsed_dataset, self.col_names)
        # computation with parameters given from GUI
        climatology_options = Options(
            climatology_start=self.climatologyStartComboBox.currentText(),
            climatology_end=self.climatologyEndComboBox.currentText(),
        )
        filtered_climatology_dataset = Dataset(self.dataset_filename, self.parsed_dataset, self.col_names, options=climatology_options)

        monitoring_options = Options(
            season_start=self.seasonStartComboBox.currentText(),
            season_end=self.seasonEndComboBox.currentText(),
        )
        monitoring_filtered_dataset = Dataset(self.dataset_filename, self.parsed_dataset, self.col_names, options=monitoring_options)

        all_options = Options(
            climatology_start=self.climatologyStartComboBox.currentText(),
            climatology_end=self.climatologyEndComboBox.currentText(),
            season_start=self.seasonStartComboBox.currentText(),
            season_end=self.seasonEndComboBox.currentText(),
        )
        filtered_dataset = Dataset(self.dataset_filename, self.parsed_dataset, self.col_names, options=all_options)
        # output files
        destination_path = os.path.join(self.dataset_source_path, self.dataset_filename)
        export_to_web_files(destination_path, self.structured_dataset, filtered_climatology_dataset, monitoring_filtered_dataset, filtered_dataset)
        renderFinishTime = time.perf_counter() - renderTime
        QMessageBox(text=f'Task completed.\nProcessing time: {renderFinishTime}').exec()

            # stats = pstats.Stats(profile)
            # stats.sort_stats(pstats.SortKey.TIME)
            # stats.dump_stats('snakeviz.prof')
            # stats.print_stats()

    # placeholder
    def path_changed_event(self): 
        print(self.datasetInputLineEdit.text())
        if self.datasetInputLineEdit.text().__len__() != 0:
            print('valid')