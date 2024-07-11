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
import json
import traceback
# import cProfile
# import pstats

# from qgis.PyQt import uic, QtWidgets
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import QObject, QRunnable, QThreadPool, pyqtSlot, pyqtSignal

from .map_settings_dialog import MapSettingsDialog
from .year_selection_dialog import YearSelectionDialog
from .progress_dialog import ProgressDialog

from .nsmpgCore.parsers.CSVParser import parse_csv
from .nsmpgCore.structures import Dataset, Options, Properties
from .nsmpgCore.utils import (
    define_seasonal_dict, parse_timestamps, 
    get_properties_validated_year_list
    )
from .nsmpgCore.exporters.WebExporter import export_to_web_files
from .nsmpgCore.exporters.CSVExporter import export_to_csv_files
from .nsmpgCore.exporters.ImageExporter import export_to_image_files

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
        self.threadpool = QThreadPool()
        self.pending_tasks = 0

        self.year_selection_dialog = YearSelectionDialog(self)
        self.progress_dialog = ProgressDialog(self)
        self.map_settings_dialog = MapSettingsDialog(self)

        self.climatologyGroup: QGroupBox
        self.monitoringGroup: QGroupBox
        self.yearSelectionGroup: QGroupBox

        self.loadFileButton: QPushButton
        self.datasetInputLineEdit: QLineEdit
        self.importParametersButton: QPushButton
        self.importParametersLineEdit: QLineEdit
        
        self.climatologyStartComboBox: QComboBox
        self.climatologyEndComboBox: QComboBox

        self.crossYearsCheckBox: QCheckBox
        self.seasonStartComboBox: QComboBox
        self.seasonEndComboBox: QComboBox

        self.customYearsRadioButton: QRadioButton
        self.similarYearsRadioButton: QRadioButton
        self.similarYearsComboBox: QComboBox
        self.usePearsonCheckBox: QCheckBox
        self.selectYearsButton: QPushButton

        self.observedDataRadioButton: QRadioButton
        self.forecastRadioButton: QRadioButton

        self.exportWebCheckBox: QCheckBox
        self.exportImagesCheckBox: QCheckBox
        self.exportStatsCheckBox: QCheckBox
        self.exportParametersCheckBox: QCheckBox
        self.mappingButton: QPushButton

        self.datasetInfoLabel: QLabel

        self.processButton: QPushButton

        self.mappingButton.clicked.connect(self.mapping_button_event)

        self.crossYearsCheckBox.stateChanged.connect(self.cross_years_cb_changed_event)
        self.customYearsRadioButton.toggled.connect(self.year_selection_rb_event)
        self.similarYearsRadioButton.toggled.connect(self.year_selection_rb_event)
        self.selectYearsButton.clicked.connect(self.select_years_btn_event)

        self.loadFileButton.clicked.connect(self.load_file_btn_event)
        self.importParametersButton.clicked.connect(self.import_parameters_btn_event)
        self.processButton.clicked.connect(self.process_btn_event)

    def update_fields(self, options: Options):
        self.crossYearsCheckBox.setChecked(options.cross_years)
        year_ids = get_properties_validated_year_list(self.dataset_properties, self.crossYearsCheckBox.isChecked())
        sub_season_ids = define_seasonal_dict(self.crossYearsCheckBox.isChecked())

        self.climatologyStartComboBox.setEnabled(True)
        self.climatologyStartComboBox.clear()
        self.climatologyStartComboBox.addItems(year_ids)
        if '1991' in year_ids:
            self.climatologyStartComboBox.setCurrentText('1991')
        else:
            self.climatologyStartComboBox.setCurrentText(options.climatology_start)
        self.climatologyEndComboBox.setEnabled(True)
        self.climatologyEndComboBox.clear()
        self.climatologyEndComboBox.addItems(year_ids)
        if '2020' in year_ids:
            self.climatologyEndComboBox.setCurrentText('2020')
        else:
            self.climatologyEndComboBox.setCurrentText(options.climatology_end)

        self.seasonStartComboBox.setEnabled(True)
        self.seasonStartComboBox.clear()
        self.seasonStartComboBox.addItems(sub_season_ids)
        self.seasonStartComboBox.setCurrentText(options.season_start)
        self.seasonEndComboBox.setEnabled(True)
        self.seasonEndComboBox.clear()
        self.seasonEndComboBox.addItems(sub_season_ids)
        self.seasonEndComboBox.setCurrentText(options.season_end)

        self.importParametersLineEdit.setEnabled(True)
        self.importParametersButton.setEnabled(True)
        self.customYearsRadioButton.setEnabled(True)
        self.similarYearsRadioButton.setEnabled(True)
        self.crossYearsCheckBox.setEnabled(True)
        self.processButton.setEnabled(True)

        if isinstance(options.selected_years, list):
            self.customYearsRadioButton.setChecked(True)
            self.selectYearsButton.setEnabled(True)
            self.similarYearsComboBox.setEnabled(False)
            self.usePearsonCheckBox.setEnabled(False)
        self.year_selection_dialog.updateYearsList(year_ids)
        self.year_selection_dialog.selected_years = options.selected_years
        self.year_selection_dialog.update_selection()

        self.similarYearsComboBox.clear()
        self.similarYearsComboBox.addItems([str(y) for y in range(1, self.dataset_properties.season_quantity+1)])
        if isinstance(options.selected_years, str):
            self.similarYearsRadioButton.setChecked(True)
            self.similarYearsComboBox.setEnabled(True)
            self.similarYearsComboBox.setCurrentText(options.selected_years)
            self.usePearsonCheckBox.setEnabled(True)
            self.selectYearsButton.setEnabled(False)
        self.usePearsonCheckBox.setChecked(options.use_pearson)

        self.observedDataRadioButton.setEnabled(True)
        self.forecastRadioButton.setEnabled(True)
        if options.is_forecast: self.forecastRadioButton.setChecked(True)
        else: self.observedDataRadioButton.setChecked(True)

        self.exportWebCheckBox.setEnabled(True)
        self.exportWebCheckBox.setChecked(options.output_web)
        self.exportImagesCheckBox.setEnabled(True)
        self.exportImagesCheckBox.setChecked(options.output_images)
        self.exportStatsCheckBox.setEnabled(True)
        self.exportStatsCheckBox.setChecked(options.output_stats)
        self.exportParametersCheckBox.setEnabled(True)
        self.exportParametersCheckBox.setChecked(options.output_parameters)
        self.mappingButton.setEnabled(True)

    # function that reads the dataset from a file.
    def load_file_btn_event(self): 
        # path reading
        temp_dataset_source = QFileDialog.getOpenFileName(self, 'Open dataset file', None, "CSV files (*.csv)")[0]
        if temp_dataset_source == "":
            QMessageBox.warning(self, "Warning", 
                                'No dataset was selected.', 
                                QMessageBox.Ok)
            return
        self.selected_source = temp_dataset_source
        self.dataset_source_path = os.path.normpath(os.path.dirname(self.selected_source))
        self.dataset_filename = ''.join(os.path.basename(self.selected_source).split('.')[:-1])

        # parse dataset
        try:
            self.parsed_dataset, self.col_names, has_duplicates = parse_csv(self.selected_source)
            self.dataset_properties = Properties(parse_timestamps(self.col_names))
        except Exception as e:
            QMessageBox.critical(self, "Error", f'The dataset could not be read.\n\n{str(e)}\n\n{traceback.format_exc()}', QMessageBox.Ok)
            return
        if has_duplicates:
            QMessageBox.warning(self, "Warning", 
                                'Duplicated place names have been found.\nThe program might produce unexpected results.', 
                                QMessageBox.Ok)
        default_options = Options(dataset_properties=self.dataset_properties)

        # set form fields content from data
        self.datasetInputLineEdit.setText(self.selected_source)

        self.update_fields(default_options)
        self.update_dialog_info(self.dataset_properties)

    # function to allow the computation of the required data, such as accumulation, ensemble, stats, percentiles, etc
    def process_btn_event(self):
        # invalid input handling
        if self.climatologyStartComboBox.currentIndex() > self.climatologyEndComboBox.currentIndex():
            QMessageBox.critical(self, "Error", 
                                 'The start of the climatology must be before the end of the climatology', 
                                 QMessageBox.Ok)
            return
        if self.seasonStartComboBox.currentIndex() > self.seasonEndComboBox.currentIndex():
            QMessageBox.critical(self, "Error", 
                                 'The start of the season must be before the end of the season.', 
                                 QMessageBox.Ok)
            return

        # path reading
        self.destination_path = os.path.normpath(QFileDialog.getExistingDirectory(self, 'Save results', self.dataset_source_path))
        if self.destination_path == ".":
            QMessageBox.warning(self, "Warning", 
                                'No export folder was selected.', 
                                QMessageBox.Ok)
            return
        
        # ask for creating subfolder
        dlg = QMessageBox.information(self, "Create new folder?", 
                            f'Do you want to create a folder for the report files?\nThe folder {self.dataset_filename} at the path {self.destination_path} will be created.', 
                            QMessageBox.Yes, QMessageBox.No)
        if dlg == QMessageBox.Yes:
            self.destination_path = os.path.join(self.destination_path, self.dataset_filename)
        
        # with cProfile.Profile() as profile:
        self.renderTime = time.perf_counter()
        # computation with parameters given from GUI
        options = Options(
            climatology_start=self.climatologyStartComboBox.currentText(),
            climatology_end=self.climatologyEndComboBox.currentText(),
            season_start=self.seasonStartComboBox.currentText(),
            season_end=self.seasonEndComboBox.currentText(),
            cross_years=self.crossYearsCheckBox.isChecked(),
            selected_years=self.year_selection_dialog.selected_years if self.customYearsRadioButton.isChecked() else self.similarYearsComboBox.currentText(),
            is_forecast=self.forecastRadioButton.isChecked(),
            use_pearson=self.usePearsonCheckBox.isChecked(),
            output_web=self.exportWebCheckBox.isChecked(),
            output_images=self.exportImagesCheckBox.isChecked(),
            output_stats=self.exportStatsCheckBox.isChecked(),
            output_parameters=self.exportParametersCheckBox.isChecked(),
        )
        self.structured_dataset = Dataset(self.dataset_filename, self.parsed_dataset, self.col_names, options)
        
        # output files
        self.progress_dialog.show()
        self.pending_tasks = self.exportStatsCheckBox.isChecked() + \
                             self.exportWebCheckBox.isChecked() +\
                             self.exportImagesCheckBox.isChecked()
        workers: list[Worker] = []
        if self.exportStatsCheckBox.isChecked():
            workers.append(Worker(export_to_csv_files, self.destination_path, self.structured_dataset))
        if self.exportWebCheckBox.isChecked():
            workers.append(Worker(export_to_web_files, self.destination_path, self.structured_dataset))
        if self.exportParametersCheckBox.isChecked():
            json_data = json.dumps(options.__dict__)
            if isinstance(json_data, bytes): json_data = json_data.decode()
            os.makedirs(self.destination_path, exist_ok=True)
            with open(f'{self.destination_path}/Parameters.json', 'w') as js_data_wrapper:
                js_data_wrapper.write(json_data)
        if self.exportImagesCheckBox.isChecked():
            workers.append(Worker(export_to_image_files, self.destination_path, self.structured_dataset))
        for worker in workers:
            worker.signal_emitter.finished.connect(self.progress_dialog.update)
            self.threadpool.start(worker)

            # stats = pstats.Stats(profile)
            # stats.sort_stats(pstats.SortKey.TIME)
            # stats.dump_stats('snakeviz.prof')

    def import_parameters_btn_event(self) -> None:
        # path reading
        temp_parameters_source = QFileDialog.getOpenFileName(self, 'Open parameters file', None, "JSON files (*.json)")[0]
        if temp_parameters_source == "": 
            QMessageBox.warning(self, "Warning", 
                                'No dataset was selected.', 
                                QMessageBox.Ok)
            return
        self.parameters_source = temp_parameters_source
        try:
            with open(self.parameters_source, 'r') as json_file:
                parameters = json.load(json_file)
            options = Options()
            options.overwrite(parameters)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not load parameters from {self.parameters_source}.\n\n{str(e)}\n\n{traceback.format_exc()}')
            return
        self.importParametersLineEdit.setText(self.parameters_source)
        self.update_fields(options)

    def cross_years_cb_changed_event(self):
        sub_season_ids = define_seasonal_dict(self.crossYearsCheckBox.isChecked())
        year_list = get_properties_validated_year_list(self.dataset_properties, self.crossYearsCheckBox.isChecked())
        options = Options(
            climatology_start=year_list[0],
            climatology_end=year_list[-1],
            season_start=sub_season_ids[0],
            season_end=sub_season_ids[-1],
            cross_years=self.crossYearsCheckBox.isChecked(),
            selected_years=year_list,
            is_forecast=self.forecastRadioButton.isChecked(),
            use_pearson=self.usePearsonCheckBox.isChecked(),
            output_web=self.exportWebCheckBox.isChecked(),
            output_images=self.exportImagesCheckBox.isChecked(),
            output_stats=self.exportStatsCheckBox.isChecked(),
            output_parameters=self.exportParametersCheckBox.isChecked(),
            )
        self.update_fields(options)

    def year_selection_rb_event(self):
        if self.customYearsRadioButton.isChecked():
            self.selectYearsButton.setEnabled(True)
            self.similarYearsComboBox.setEnabled(False)
            self.usePearsonCheckBox.setEnabled(False)
        elif self.similarYearsRadioButton.isChecked():
            self.similarYearsComboBox.setEnabled(True)
            self.usePearsonCheckBox.setEnabled(True)
            self.selectYearsButton.setEnabled(False)

    def select_years_btn_event(self):
        self.year_selection_dialog.show()

    def mapping_button_event(self):
        self.map_settings_dialog.show()

    def update_dialog_info(self, dataset_properties: Properties):
        dg_text = \
f'''First Year: {dataset_properties.year_ids[0]}
Last Year: {dataset_properties.year_ids[-1]}
Current Year: {dataset_properties.current_season_id}
Dekads in Current Year: {dataset_properties.current_season_length}'''
        self.datasetInfoLabel.setText(dg_text)

class Worker(QRunnable):
    def __init__(self, f, *args):
        super(Worker, self).__init__()
        self.signal_emitter = WorkerSignalEmitter()
        self.f = f
        self.args = args

    @pyqtSlot()
    def run(self):
        self.f(*self.args)
        self.signal_emitter.finished.emit()

class WorkerSignalEmitter(QObject):
    finished = pyqtSignal()