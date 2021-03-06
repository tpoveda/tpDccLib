#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains generic functionality when dealing with projects
"""

from __future__ import print_function, division, absolute_import

import os
import logging

from Qt.QtGui import QPixmap

from tpDcc.core import options, consts
from tpDcc.managers import resources
from tpDcc.libs.python import path, folder, settings

LOGGER = logging.getLogger('tpDcc-core')


class ProjectData(options.OptionObject):
    def __init__(self, name, project_path, settings, options):
        super(ProjectData, self).__init__(option_settings=options)

        self._name = name
        self._project_path = project_path
        self._settings = settings

    # ================================================================================================
    # ======================== PROPERTIES
    # ================================================================================================

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._project_path

    @property
    def full_path(self):
        return path.join_path(self._project_path, self._name)

    @property
    def settings(self):
        return self._settings

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def _setup_options(self):

        super(ProjectData, self)._setup_options()

        self._option_settings.set_directory(os.path.dirname(self.get_project_file()), 'options.json')

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def get_project_file(self):
        """
        Returns path where project file is located
        :return: str
        """

        return path.join_path(self.full_path, consts.PROJECTS_NAME)

    def get_project_image(self):
        """
        Returns the image used by the project
        :return: QPixmap
        """

        from tpDcc.libs.qt.core import image

        if not self._settings:
            self._load_project()

        project_file = self.get_project_file()
        if not self._settings.has_settings():
            LOGGER.warning('No valid project data found on Project Data File: {}'.format(project_file))

        encoded_image = self._settings.get('image')
        if not encoded_image:
            return

        encoded_image = encoded_image.encode('utf-8')
        return QPixmap.fromImage(image.base64_to_image(encoded_image))

    def update_project(self):

        if not self._settings:
            self._load_project()

        project_file = self.get_project_file()
        if not self._settings.has_settings():
            LOGGER.warning('No valid project data found on Project Data File: {}'.format(project_file))

        self._name = self._settings.get('name')
        self._project_path = path.get_dirname(path.get_dirname(project_file))

    def set_project_image(self, image_path):
        """
        Updates project image icon
        :param image_path: str, path that points to the image of the new project icon
        """

        from tpDcc.libs.qt.core import image

        if not os.path.isfile(image_path):
            LOGGER.warning('Given image path "{}" is not valid!'.format(image_path))
            return False

        if not self._settings:
            self._load_project()

        project_file = self.get_project_file()
        if not self._settings.has_settings():
            LOGGER.warning('No valid project data found on Project Data File: {}'.format(project_file))

        self._settings.set('image', image.image_to_base64(image_path))

        return True

    def create_project(self):
        project_full_path = self.full_path
        if path.is_dir(project_full_path):
            LOGGER.warning('Project Path {} already exists! Choose another one ...'.format(project_full_path))
            return

        folder.create_folder(name=self.name, directory=self._project_path)
        self._set_default_settings()

        return self

    def create_folder(self, name, relative_path=None):
        if relative_path is None:
            folder.create_folder(name=name, directory=self.full_path)
        else:
            folder.create_folder(name=name, directory=path.join_path(self.full_path, relative_path))

    def _load_project(self):
        self._set_default_settings()
        self._setup_options()

    def _set_settings_path(self, folder_path):
        if not self._settings:
            self._load_project()

        project_file_path = self.get_project_file()
        project_file = path.get_basename(project_file_path)
        self._settings.set_directory(folder_path, project_file)

    def _set_options_path(self, folder_path):
        if not self._option_settings:
            self._load_project()

        self._option_settings.set_directory(folder_path, 'options.json')

    def _set_default_settings(self):

        from tpDcc.libs.qt.core import image

        project_file_path = self.get_project_file()
        project_path = path.get_dirname(project_file_path)
        self._settings = settings.JSONSettings()
        self._set_settings_path(project_path)
        self._settings.set('version', '0.0.0')
        self._settings.set('name', self.name)
        self._settings.set('path', self._project_path)
        self._settings.set('full_path', self.full_path)
        self._settings.set('image', str(image.image_to_base64(resources.get('icons', 'default', 'tpdcc.png'))))
