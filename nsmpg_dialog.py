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
# import cProfile
# import pstats

# from qgis.PyQt import uic, QtWidgets
from PyQt5 import uic
from PyQt5.QtWidgets import *

from .nsmpgCore.parsers.CSVParser import parse_csv
from .nsmpgCore.structures import Dataset, Options, Properties
from .nsmpgCore.commons import define_seasonal_dict, parse_timestamps, get_cross_years, get_properties_validated_year_list, yearly_periods, comparison_methods_list
from .nsmpgCore.exporters.WebExporter import export_to_web_files
from .nsmpgCore.exporters.CSVExporter import export_to_csv_files
from .nsmpgCore.exporters.ImageExporter import export_to_image_files

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'nsmpg_dialog_base.ui'))
YEAR_SELECTION_DIALOG_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'year_selection_dialog.ui'))
ABOUT_DIALOG_CLASS,_ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'about_dialog.ui'))


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
        self.year_selection_dialog = YearSelectionDialog(self)
        self.about_dialog = AboutDialog(self)

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
        self.comparisonMethodComboBox: QComboBox
        self.selectYearsButton: QPushButton

        self.observedDataRadioButton: QRadioButton
        self.forecastRadioButton: QRadioButton

        self.exportWebCheckBox: QCheckBox
        self.exportImagesCheckBox: QCheckBox
        self.exportStatsCheckBox: QCheckBox
        self.exportParametersCheckBox: QCheckBox

        self.aboutButton: QPushButton

        self.processButton: QPushButton

        self.crossYearsCheckBox.stateChanged.connect(self.cross_years_cb_changed_event)
        self.customYearsRadioButton.toggled.connect(self.year_selection_rb_event)
        self.similarYearsRadioButton.toggled.connect(self.year_selection_rb_event)
        self.selectYearsButton.clicked.connect(self.select_years_btn_event)

        self.loadFileButton.clicked.connect(self.load_file_btn_event)
        self.importParametersButton.clicked.connect(self.import_parameters_btn_event)
        self.processButton.clicked.connect(self.process_btn_event)
        self.aboutButton.clicked.connect(self.about_btn_event)

    def update_fields(self, options: Options):
        self.crossYearsCheckBox.setChecked(options.cross_years)
        year_ids = get_properties_validated_year_list(self.dataset_properties, self.crossYearsCheckBox.isChecked())
        sub_season_ids = define_seasonal_dict(self.crossYearsCheckBox.isChecked())

        self.climatologyStartComboBox.setEnabled(True)
        self.climatologyStartComboBox.clear()
        self.climatologyStartComboBox.addItems(year_ids)
        self.climatologyStartComboBox.setCurrentText(options.climatology_start)
        self.climatologyEndComboBox.setEnabled(True)
        self.climatologyEndComboBox.clear()
        self.climatologyEndComboBox.addItems(year_ids)
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
            self.comparisonMethodComboBox.setEnabled(False)
        self.year_selection_dialog.updateYearsList(year_ids)
        self.year_selection_dialog.selected_years = options.selected_years
        self.year_selection_dialog.update_selection()

        self.similarYearsComboBox.clear()
        self.similarYearsComboBox.addItems([str(y) for y in range(1, self.dataset_properties.season_quantity+1)])
        if isinstance(options.selected_years, str):
            self.similarYearsRadioButton.setChecked(True)
            self.similarYearsComboBox.setEnabled(True)
            self.similarYearsComboBox.setCurrentText(options.selected_years)
            self.comparisonMethodComboBox.setEnabled(True)
            self.comparisonMethodComboBox.setCurrentText(options.comparison_method)
            self.selectYearsButton.setEnabled(False)
        self.comparisonMethodComboBox.clear()
        self.comparisonMethodComboBox.addItems(comparison_methods_list)
        self.comparisonMethodComboBox.setCurrentText(options.comparison_method)

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

    # function that reads the dataset from a file.
    def load_file_btn_event(self): 
        # path reading
        self.selected_source = QFileDialog.getOpenFileName(self, 'Open dataset file', None, "CSV files (*.csv)")[0]
        if self.selected_source == "": return
        self.dataset_source_path = os.path.normpath(os.path.dirname(self.selected_source))
        self.dataset_filename = ''.join(os.path.basename(self.selected_source).split('.')[:-1])

        # parse dataset
        try:
            self.parsed_dataset, self.col_names, has_duplicates = parse_csv(self.selected_source)
            self.dataset_properties = Properties(parse_timestamps(self.col_names))
        except Exception as e:
            QMessageBox.critical(self, "Error", f'The dataset could not be read.\n\n{str(e)}', QMessageBox.Ok)
            return
        if has_duplicates:
            QMessageBox.warning(self, "Warning", 
                                'Duplicated place names have been found.\nThe program might produce unexpected results.', 
                                QMessageBox.Ok)
        default_options = Options(dataset_properties=self.dataset_properties)

        # set form fields content from data
        self.datasetInputLineEdit.setText(self.selected_source)

        self.update_fields(default_options)

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
        destination_path = QFileDialog.getExistingDirectory(self, 'Open dataset file', self.dataset_source_path)[0]
        if self.selected_source == "": return
        # check if the selected directory exists and create it if necessary
        path_with_filename = os.path.join(destination_path, self.dataset_filename)
        if path_with_filename not in destination_path:
            destination_path = path_with_filename
        
        # with cProfile.Profile() as profile:
        renderTime = time.perf_counter()
        # computation with parameters given from GUI
        options = Options(
            climatology_start=self.climatologyStartComboBox.currentText(),
            climatology_end=self.climatologyEndComboBox.currentText(),
            season_start=self.seasonStartComboBox.currentText(),
            season_end=self.seasonEndComboBox.currentText(),
            cross_years=self.crossYearsCheckBox.isChecked(),
            selected_years=self.year_selection_dialog.selected_years if self.customYearsRadioButton.isChecked() else self.similarYearsComboBox.currentText(),
            is_forecast=self.forecastRadioButton.isChecked(),
            comparison_method=self.comparisonMethodComboBox.currentText(),
            output_web=self.exportWebCheckBox.isChecked(),
            output_images=self.exportImagesCheckBox.isChecked(),
            output_stats=self.exportStatsCheckBox.isChecked(),
            output_parameters=self.exportParametersCheckBox.isChecked(),
        )
        self.structured_dataset = Dataset(self.dataset_filename, self.parsed_dataset, self.col_names, options)
        
        # output files
        destination_path = os.path.join(self.dataset_source_path, self.dataset_filename)
        if self.exportStatsCheckBox.isChecked():
            export_to_csv_files(destination_path, self.structured_dataset)
        if self.exportWebCheckBox.isChecked():
            export_to_web_files(destination_path, self.structured_dataset)
        if self.exportParametersCheckBox.isChecked():
            json_data = json.dumps(options.__dict__)
            if isinstance(json_data, bytes): json_data = json_data.decode()
            os.makedirs(destination_path, exist_ok=True)
            with open(f'{destination_path}/Parameters.json', 'w') as js_data_wrapper:
                js_data_wrapper.write(json_data)
        if self.exportImagesCheckBox.isChecked():
            export_to_image_files(destination_path, self.structured_dataset)
        renderFinishTime = time.perf_counter() - renderTime
        QMessageBox(text=f'Task completed.\nProcessing time: {renderFinishTime}').exec()

            # stats = pstats.Stats(profile)
            # stats.sort_stats(pstats.SortKey.TIME)
            # stats.dump_stats('snakeviz.prof')

    def import_parameters_btn_event(self) -> None:
        # path reading
        parameters_source = QFileDialog.getOpenFileName(self, 'Open dataset file', None, "JSON files (*.json)")[0]
        if parameters_source == "": return

        try:
            with open(parameters_source, 'r') as json_file:
                parameters = json.load(json_file)
            options = Options()
            options.overwrite(parameters)
        except:
            QMessageBox.critical(self, 'Error', f'Could not load parameters from {parameters_source}')
            return
        self.importParametersLineEdit.setText(parameters_source)
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
            comparison_method=self.comparisonMethodComboBox.currentText(),
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
            self.comparisonMethodComboBox.setEnabled(False)
        elif self.similarYearsRadioButton.isChecked():
            self.similarYearsComboBox.setEnabled(True)
            self.comparisonMethodComboBox.setEnabled(True)
            self.selectYearsButton.setEnabled(False)

    def select_years_btn_event(self):
        self.year_selection_dialog.show()

    def about_btn_event(self):
        self.about_dialog.show()

class YearSelectionDialog(QDialog, YEAR_SELECTION_DIALOG_CLASS):
    def __init__(self, parent=None):
        super(YearSelectionDialog, self).__init__(parent)
        self.setupUi(self)

        self.yearsFrame: QFrame
        self.yearsLayout: QGridLayout
        self.selectAllCheckBox: QCheckBox
        self.select_all_state = False
        self.year_combo_boxes: list[QCheckBox] = []
        self.selected_years: list[str] = []

        self.selectAllCheckBox.clicked.connect(self.select_all_cb_event)

    def updateYearsList(self, year_list):
        self.clear_years_layout()
        self.selectAllCheckBox.setChecked(False)
        cb_list = []
        col_n = 0
        row_n = 0
        for year in year_list:
            check_box = QCheckBox(year)
            check_box.clicked.connect(self.year_combo_boxes_changed)
            self.yearsLayout.addWidget(check_box, row_n, col_n)
            cb_list.append(check_box)
            col_n += 1
            if col_n == 4:
                row_n += 1
                col_n = 0
        self.year_combo_boxes = cb_list
    
    def select_all_cb_event(self):
        for cb in self.year_combo_boxes:
            cb.setChecked(self.selectAllCheckBox.isChecked())

    def update_selection(self):
        all_checked = True
        for cb in self.year_combo_boxes:
            if cb.text() in self.selected_years:
                cb.setChecked(True)
            else:
                cb.setChecked(False)
                all_checked &= False
        self.selectAllCheckBox.setChecked(all_checked)

    def accept(self) -> None:
        self.selected_years = []
        for cb in self.year_combo_boxes:
            if cb.isChecked():
                self.selected_years.append(cb.text())
        self.select_all_state = self.selectAllCheckBox.isChecked()
        super(YearSelectionDialog, self).accept()

    def reject(self) -> None:
        self.update_selection()
        super(YearSelectionDialog, self).reject()

    def year_combo_boxes_changed(self):
        for cb in self.year_combo_boxes:
            if cb.isChecked() == False:
                self.selectAllCheckBox.setChecked(False)
                return
        self.selectAllCheckBox.setChecked(True)

    def clear_years_layout(self):
        while self.yearsLayout.count():
            child = self.yearsLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

class AboutDialog(QDialog, ABOUT_DIALOG_CLASS):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)
