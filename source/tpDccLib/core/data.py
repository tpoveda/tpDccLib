#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base definitions to handle DCC data
"""

from __future__ import print_function, division, absolute_import

import os
import uuid
from collections import OrderedDict

from tpPyUtils import decorators, path, fileio, folder, settings


class DataTypes(object):
    """
    Class that defines different data types supported by DCCs
    """

    Unknown = 'Unknown'
    JSON = 'JSON'


class DataExtensions(object):
    """
    Class that defines different data extensions supported by DCCs
    """

    FileDataExtension = 'data'


class Data(object):
    """
    Base class for data objects that includes functions for save and load data
    """

    def __init__(self, name=None, data_id=None):
        self._data = OrderedDict()
        self._id = data_id or uuid.uuid4()
        self.file_filter = 'All Files (*.*)'
        self._name = name
        if not name:
            self._name = self.get_data_title()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @staticmethod
    def get_data_type():
        """
        This function should be override in each derived data class
        Returns the data of type
        :return: str
        """

        return DataTypes.Unknown

    @classmethod
    def is_type_match(cls, data_type):
        """
        Returns whether the given type is the same type of the file or not
        :param data_type: str
        :return: bool
        """

        return data_type == cls.get_data_type()

    @decorators.abstractmethod
    def build_data(self):
        """
        From the given keyword arguments, the data will be generated
        """

        pass

    @decorators.abstractmethod
    def rebuild(self):
        """
        Already build is recreated from the given keyword arguments
        """

        pass

    # region Public Functions
    def set_name(self, new_name):
        """
        Set the name of the data
        """

        self._name = new_name

    def get_data_name(self):
        """
        Returns the name of the data
        :return: str
        """

        return self._name

    def get_data_title(self):
        """
        This function should be override in each derived data class
        Returns the title used by the data
        :return:
        """

        return self.name or 'Unknown Data'

    def reset(self):
        """
        Reset data object
        """

        self.__init__()


class FileData(Data, object):
    """
    Class used to define data stored in disk files
    """

    def __init__(self, name=None, path=None):
        super(FileData, self).__init__(name=name)

        self.extension = self.get_data_extension()
        self.directory = path
        self.settings = settings.JSONSettings()
        self.file = None
        self._sub_folder = None

    # region Static Functions
    @staticmethod
    def get_data_extension():
        """
        Returns extension of the file
        Should be override on derived classes
        :return: str
        """

        return DataExtensions.FileDataExtension
    # endregion

    # region Public Functions
    def set_directory(self, directory):
        """
        Sets the directory where data file is stored
        :param directory: str
        """

        self.directory = directory
        self.settings.set_directory(self.directory, 'data.json')

        if not self.name:
            self.name = self.settings.get('name')

        self.get_sub_folder()

        if self.extension:
            self.file_path = path.join_path(directory, '{}.{}'.format(self.name, self.extension))
        else:
            self.file_path = path.join_path(directory, self.name)

    def create(self):
        """
        Creates file
        """

        self.file = fileio.create_file(filename='{}.{}'.format(self.name, self.extension), directory=self.directory)

    def get_file(self):
        """
        Returns file path where file is stored taking into account the sub folder
        :return: str
        """

        data_directory = self.directory
        data_name = self._get_file_name()

        if self._sub_folder:
            data_directory = path.join_path(self.directory, '.sub/{}'.format(self._sub_folder))

        file_path = path.join_path(data_directory, data_name)

        return file_path

    def get_file_direct(self, sub_folder=None):
        """
        Returns the file path where file is stored and optionally the sub folder is a name is given
        :param sub_folder: str, name of subfolder (optional)
        :return:
        """

        data_directory = self.directory
        data_name = self._get_file_name()

        if sub_folder:
            data_directory = path.join_path(self.directory, '.sub/{}'.format(sub_folder))

        file_path = path.join_path(data_directory, data_name)

        return file_path

    def get_folder(self):
        """
        Returns folder where file is stored
        :return: str
        """

        return self.directory

    def get_sub_folder(self):
        """
        Returns file sub folder
        :return: str
        """

        folder_name = self.settings.get('sub_folder')
        if self.directory:
            if not path.is_dir(path.join_path(self.directory, '.sub/{}'.format(folder_name))):
                self.set_sub_folder('')
                return

        self._sub_folder = folder_name

        return folder_name

    def set_sub_folder(self, folder_name):
        """
        Sets file sub folder
        :param folder_name: str
        """

        self._sub_folder = folder_name
        sub_folder = path.join_path(self.directory, '.sub/{}'.format(folder_name))
        if path.is_dir(sub_folder):
            self.settings.set('sub_folder', folder_name)

    def rename(self, new_name):
        """
        Renames the file
        :param new_name: str, new file name
        :return: str, new file name
        """

        old_name = self.name
        if old_name == new_name:
            return
        old_file_path = path.join_path(self.directory, '{}.{}'.format(old_name, self.extension))
        self.name = new_name
        if path.is_file(old_file_path) or path.is_dir(old_file_path):
            folder.rename_folder(directory=old_file_path, name=self._get_file_name())
            return self._get_file_name()

    def _get_file_name(self):
        name = self.name
        if self.extension:
            return '{0}.{1}'.format(self.name, self.extension)
        else:
            return name
